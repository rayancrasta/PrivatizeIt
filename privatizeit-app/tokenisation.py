import hashlib
import random
import string
import crud
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.backends import default_backend


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

def generate_rsakeys():
    private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=1024,
    )
    
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_key_pem.decode('utf-8'), public_key_pem.decode('utf-8')
    
def encrypt_original(public_key:str,original_value:str) -> str:
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

def decrypt_to_original(encrypted_value_string:str,private_key_string:str):
    # Deserialize the private key
    private_key = serialization.load_pem_private_key(
        private_key_string.encode(),
        password=None,
        backend=default_backend()
    )

    
    print("Encrypted value string: "+encrypted_value_string)
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

     