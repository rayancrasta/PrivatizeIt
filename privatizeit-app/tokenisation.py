import hashlib
import random
import string
import crud
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.backends import default_backend
from crud_mongodb import add_domain_policy,get_tokenisation_policy_id_from_name,get_tokenisation_pname_from_policyid
import models, tokenisation, schemas
from validaton import validate_user_input,fetch_schema

def get_random_salt(length=16):
    # Random string of fixed length
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def tokenise_number(number): 
    number_str = str(number)
    # Generate a random salt
    salt = get_random_salt()
    # Tokenize number to a fixed length using a hash function with salt
    hashed = hashlib.sha256((number_str + salt).encode()).hexdigest()[:len(number_str)]
    return ''.join(str((int(char, 16) % 10)) for char in hashed)

def tokenise_string(value):
    # Generate a random salt
    salt = get_random_salt()
    # Tokenize string to a deterministic random string of the same length using salt
    hashed = hashlib.sha256((value + salt).encode()).hexdigest()
    return hashed[:len(value)]

def tokenise_email(email):
    user, domain = email.split('@')
    tokenized_user = tokenise_string(user)
    tokenized_domain = tokenise_string(domain.split('.')[0])
    return f"{tokenized_user}@{tokenized_domain}.domain"

def generate_rsakeys(key_pass:str):
    private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=1024,
    )
    
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(key_pass.encode())
    )
    
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_key_pem.decode('utf-8'), public_key_pem.decode('utf-8')
    
def encrypt_original(public_key:str,original_value:str) -> str:
    original_value = str(original_value)
    if isinstance(public_key,str):
        public_key = public_key.encode() # to bytes
    public_key = serialization.load_pem_public_key(public_key,backend=default_backend())
    
    # Encrypt the original value
    encrypted_value = public_key.encrypt(
        original_value.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return encrypted_value.hex()

def decrypt_to_original(encrypted_value_string:str,private_key_string:str,key_pass:str):
    # Deserialize the private key
    private_key = serialization.load_pem_private_key(
        private_key_string.encode(),
        password=key_pass.encode(),
        backend=default_backend()
    )

    # print("Encrypted value string: "+encrypted_value_string)
    # Convert to bytes
    encrypted_value = bytes.fromhex(encrypted_value_string)

    # Decrypt the encrypted value
    decrypted_value = private_key.decrypt(
        encrypted_value,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted_value.decode() #to string

async def detokenisation_logic(db,user_input:schemas.UserInputDT):
    #Get name of domain from the MonogDB
    try:
        tokenisation_pname = await get_tokenisation_pname_from_policyid(user_input.tokenisation_policy_id)
    except Exception as e:
        raise "Domain Name Fetch failed"+str(e)
    
    #Get table from the tokenisation_pname
    table = models.create_or_get_tokenised_data_class(tokenisation_pname)
    
    try:
        private_key = crud.get_private_key(user_input.tokenisation_policy_id,db)
    except Exception as e:
       raise "Private key fetch error : "+str(e)
   
    # Fetch the tokenization policy
    try:
        schema = await fetch_schema(user_input.tokenisation_policy_id)
        if schema is None:
            raise "Tokenization policy fetch failed"
    except Exception as e:
        raise "Tokenization policy fetch failed"
    
    # Convert the policy fields to a set for quick lookup
    policy_fields = [field.field_name for field in schema.fields]
    # print("Policy: ",policy_fields)
    
    #Get original values
    try:
        original_fields = {}
        
        for field_name,tokenised_value in user_input.fields.items():
            if field_name in policy_fields:
                try:
                    encrypted_value = crud.get_encrypted_value(db,table,tokenised_value)
                except Exception as e:
                    raise "Encrypted value fetch error:"+str(e)
                
                if encrypted_value != "Not Found":
                    #Decrypt the value 
                    try:
                        original_value = tokenisation.decrypt_to_original(encrypted_value,private_key,user_input.key_pass)
                    except Exception as e:
                        raise "Decrypt to original error: "+str(e)
                    
                    original_fields[field_name] = original_value
                else:
                    original_fields[field_name] = "Not Found"
            else:
                original_fields[field_name] = tokenised_value  
        return original_fields
    except Exception as e:
        raise e
    
async def tokenisation_logic(db,user_input:schemas.UserInputT):
#Get name of domain from the MonogDB
    try:
        tokenisation_pname = await get_tokenisation_pname_from_policyid(user_input.tokenisation_policy_id)
    except Exception as e:
        raise "Domain Name Fetch failed"+str(e)
    
    #Filter the values to only schema values for validation
    filtered_values = {}
    
    # Fetch the tokenization policy
    try:
        schema = await fetch_schema(user_input.tokenisation_policy_id)
        if schema is None:
            raise "Tokenization policy fetch failed"+str(e)
    except Exception as e:
        raise "Tokenization policy fetch failed"+str(e)
    
    # Convert the policy fields to a set for quick lookup
    policy_fields = [field.field_name for field in schema.fields]
    # print("Policy: ",policy_fields)
    #Get the values to tokenise only in the filtered list    
    for field_name,fieldvalue in user_input.fields.items():
        if field_name in policy_fields:
            filtered_values[field_name]=fieldvalue    
    
    #Validate the data
    try:
        validated_data = await validate_user_input(user_input.tokenisation_policy_id,schema, filtered_values)
        # print(validated_data)
        if not validated_data:
            # print("Schema Validation Failed")
            raise "Validation failed"+str(e)
            
    except Exception as e:
        raise "Validation Failed"+str(e)
    # print("Schema Validation succesfull")
    

    #Get the public key from the request
    public_key = user_input.domain_key  
    
    #Tokenise the data and save in DB
    #Get table from the tokenisation_pname
    table = models.create_or_get_tokenised_data_class(tokenisation_pname)
    tokenised_data = {}
    # print(user_input.fields.items())
    try:
        for field_name,original_value in user_input.fields.items():
            if field_name in policy_fields:
                # print(original_value)
                if field_name == "email":
                    tokenised_value = tokenisation.tokenise_email(original_value)
                elif str(original_value).isdigit():
                    tokenised_value = tokenisation.tokenise_number(str(original_value))
                else:
                    tokenised_value = tokenisation.tokenise_string(original_value)
                
                encrypted_value = tokenisation.encrypt_original(public_key,original_value)
                crud.save_tokenised_data(db,table,encrypted_value,tokenised_value)
                tokenised_data[field_name] = tokenised_value
            else:
                tokenised_data[field_name] = original_value
                
        return tokenised_data

    except Exception as e:
        raise "Error tokenising record"+str(e)