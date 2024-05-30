from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, crud, tokenisation, database
from crud_mongodb import add_domain_policy,get_tokenisation_policy_id_from_name,get_tokenisation_pname_from_policyid
from typing import List,Dict, Any
from validaton import validate_user_input,fetch_schema
import crud_mongodb

database.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/create-domain-table/",status_code=201)
async def create_domain_table(tokenisation_pdata: schemas.DomainTableCreate,db: Session = Depends(get_db)):
    # Create the domain in PostgreSQL
    try:
        msg,exsists = crud.create_domaintable(db, tokenisation_pdata.tokenisation_pname, tokenisation_pdata.fields)
    except Exception as e:
        raise HTTPException(status_code=500, detail="DB"+str(e))

    print(exsists)
    #Save the policy in MongoDB
    try:
        if not exsists:
            tokenisation_policy_id = await add_domain_policy(tokenisation_pdata)
        else:
            tokenisation_policy_id = await get_tokenisation_policy_id_from_name(tokenisation_pdata.tokenisation_pname)
    except Exception as e:
        raise HTTPException(status_code=500,detail="Mongo"+str(e))
      
    if not exsists:
        #Generate the encryption keys
        private_key, public_key = tokenisation.generate_rsakeys(tokenisation_pdata.key_pass)
        try:
            crud.store_privatekey(db,tokenisation_policy_id,tokenisation_pdata.tokenisation_pname,private_key)
        except Exception as e:
            raise HTTPException(status_code=500,detail="Keys: "+str(e))  
    else:
        public_key = "-"
    
    resp_msg = f"Tokenisation Policy {tokenisation_pdata.tokenisation_pname} {msg}"
    return {'status':resp_msg,'tokenisation_policy_id': tokenisation_policy_id,'public_key':public_key}
 
@app.post("/tokenise-Single-record/", status_code=200)
async def tokenise_single_record(user_input: schemas.UserInputT = Body(...),db: Session = Depends(get_db)):
    
    #Get name of domain from the MonogDB
    try:
        tokenisation_pname = await get_tokenisation_pname_from_policyid(user_input.tokenisation_policy_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Domain Name Fetch failed")
    
    #Filter the values to only schema values for validation
    filtered_values = {}
    
    # Fetch the tokenization policy
    try:
        schema = await fetch_schema(user_input.tokenisation_policy_id)
        if schema is None:
            raise HTTPException(status_code=500, detail="Tokenization policy fetch failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Tokenization policy fetch failed")
    
    # Convert the policy fields to a set for quick lookup
    policy_fields = [field.field_name for field in schema.fields]
    print("Policy: ",policy_fields)
    #Get the values to tokenise only in the filtered list    
    for field_name,fieldvalue in user_input.fields.items():
        if field_name in policy_fields:
            filtered_values[field_name]=fieldvalue    
    
    #Validate the data
    try:
        validated_data = await validate_user_input(user_input.tokenisation_policy_id,schema, filtered_values)
        # print(validated_data)
        if not validated_data:
            print("Schema Validation Failed")
            raise HTTPException(status_code=422, detail="Validation failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail="Validation Failed")
    print("Schema Validation succesfull")
    

    #Get the public key from the request
    public_key = user_input.domain_key  
    
    #Tokenise the data and save in DB
    #Get table from the tokenisation_pname
    table = models.create_or_get_tokenised_data_class(tokenisation_pname)
    tokenised_data = {}
    print(user_input.fields.items())
    try:
        for field_name,original_value in user_input.fields.items():
            if field_name in policy_fields:
                if field_name == "email":
                    tokenised_value = tokenisation.tokenise_email(original_value)
                elif original_value.isdigit():
                    tokenised_value = tokenisation.tokenise_number(original_value)
                else:
                    tokenised_value = tokenisation.tokenise_string(original_value)
                
                encrypted_value = tokenisation.encrypt_original(public_key,original_value)
                crud.save_tokenised_data(db,table,encrypted_value,tokenised_value)
                tokenised_data[field_name] = tokenised_value
            else:
                tokenised_data[field_name] = original_value
                
        return {"result": tokenised_data}
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
      
@app.get("/detokenise-Single-record/",status_code=200)
async def detokenise_single_record(user_input: schemas.UserInputDT = Body(...),db:Session = Depends(get_db)):
    #Get name of domain from the MonogDB
    try:
        tokenisation_pname = await get_tokenisation_pname_from_policyid(user_input.tokenisation_policy_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Domain Name Fetch failed")
    
    #Get table from the tokenisation_pname
    table = models.create_or_get_tokenised_data_class(tokenisation_pname)
    
    try:
        private_key = crud.get_private_key(user_input.tokenisation_policy_id,db)
    except Exception as e:
       raise HTTPException(status_code=500, detail="Private key fetch error : "+str(e))
   
    # Fetch the tokenization policy
    try:
        schema = await fetch_schema(user_input.tokenisation_policy_id)
        if schema is None:
            raise HTTPException(status_code=500, detail="Tokenization policy fetch failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Tokenization policy fetch failed")
    
    # Convert the policy fields to a set for quick lookup
    policy_fields = [field.field_name for field in schema.fields]
    print("Policy: ",policy_fields)
    
    #Get original values
    try:
        original_fields = {}
        
        for field_name,tokenised_value in user_input.fields.items():
            if field_name in policy_fields:
                try:
                    encrypted_value = crud.get_encrypted_value(db,table,tokenised_value)
                except Exception as e:
                    raise HTTPException(status_code=500,detail="Encrypted value fetch error:"+str(e))
                
                if encrypted_value != "Not Found":
                    #Decrypt the value 
                    try:
                        original_value = tokenisation.decrypt_to_original(encrypted_value,private_key,user_input.key_pass)
                    except Exception as e:
                        raise HTTPException(status_code=500,detail="Decrypt to original error: "+str(e))
                    
                    original_fields[field_name] = original_value
                else:
                    original_fields[field_name] = "Not Found"
            else:
                original_fields[field_name] = tokenised_value
        return {"fields":original_fields}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
@app.post("/create-masking-policy/",status_code=201)
async def create_masking_policy(masking_rules: schemas.MaskingPolicyCreate = Body(...)):
    try:
        msg,id = await crud_mongodb.save_masking_policy(masking_rules)
        resp_msg = f"Masking Policy {masking_rules.masking_policy_name} {msg}"
        return {'status':resp_msg,'masking_policy_id': id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Cant save masking policy"+str(e))
    
