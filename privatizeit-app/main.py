from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, crud, tokenisation, database
from crud_mongodb import add_domain_policy,get_domain_policy_id_from_name,get_domain_name_from_policyid
from typing import List,Dict, Any
from validaton import validate_user_input

database.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/create-domain-table/",status_code=201)
async def create_domain_table(domain_data: schemas.DomainTableCreate,db: Session = Depends(get_db)):
    # Create the domain in PostgreSQL
    try:
        msg,exsists = crud.create_domaintable(db, domain_data.domain_name, domain_data.fields)
    except Exception as e:
        raise HTTPException(status_code=500, detail="DB"+str(e))

    print(exsists)
    #Save the policy in MongoDB
    try:
        if not exsists:
            domain_policy_id = await add_domain_policy(domain_data)
        else:
            domain_policy_id = await get_domain_policy_id_from_name(domain_data.domain_name)
    except Exception as e:
        raise HTTPException(status_code=500,detail="Mongo"+str(e))
      
    if not exsists:
        #Generate the encryption keys
        private_key, public_key = tokenisation.generate_rsakeys()
        try:
            crud.store_privatekey(db,domain_policy_id,domain_data.domain_name,private_key)
        except Exception as e:
            raise HTTPException(status_code=500,detail="Keys: "+str(e))  
    else:
        public_key = "-"
    
    resp_msg = f"Domain {domain_data.domain_name} {msg}"
    return {'status':resp_msg,'domain_policy_id': domain_policy_id,'public_key':public_key}

    
@app.post("/tokenise-Single-record/", status_code=200)
async def tokenise_single_record(user_input: schemas.UserInputT = Body(...),db: Session = Depends(get_db)):
    #Validate the data
    try:
        validated_data = await validate_user_input(user_input.domain_policy_id, user_input.fields)
        # print(validated_data)
        if not validated_data:
            print("Schema Validation Failed")
            raise HTTPException(status_code=422, detail="Validation failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail="Validation Failed")
    print("Schema Validation succesfull")
    
    #Get name of domain from the MonogDB
    try:
        domain_name = await get_domain_name_from_policyid(user_input.domain_policy_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Domain Name Fetch failed")
    
    #Get the public key from the request
    public_key = user_input.domain_key  
    
    #Tokenise the data and save in DB
    #Get table from the domain_name
    table = models.create_or_get_tokenised_data_class(domain_name)
    tokenised_data = {}
    print(user_input.fields.items())
    try:
        for field_name,original_value in user_input.fields.items():
            if field_name == "email":
                tokenised_value = tokenisation.tokenise_email(original_value)
            elif original_value.isdigit():
                tokenised_value = tokenisation.tokenise_number(original_value)
            else:
                tokenised_value = tokenisation.tokenise_string(original_value)
            tokenised_data[field_name] = tokenised_value
            encrypted_value = tokenisation.encrypt_original(public_key,original_value)
            crud.save_tokenised_data(db,table,encrypted_value,tokenised_value)
                
        return {"result": tokenised_data}
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
    
@app.get("/detokenise-Single-record",status_code=200)
async def detokenise_single_record(user_input: schemas.UserInputDT = Body(...),db:Session = Depends(get_db)):
    #Get name of domain from the MonogDB
    try:
        domain_name = await get_domain_name_from_policyid(user_input.domain_policy_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Domain Name Fetch failed")
    
    #Get table from the domain_name
    table = models.create_or_get_tokenised_data_class(domain_name)
    
    try:
        private_key = crud.get_private_key(user_input.domain_policy_id,db)
    except Exception as e:
       raise HTTPException(status_code=500, detail="Private key fetch error : "+str(e))
    #Get original values
    try:
        original_fields = {}
        
        for field_name,tokenised_value in user_input.fields.items():
            try:
                encrypted_value = crud.get_encrypted_value(db,table,tokenised_value)
            except Exception as e:
                raise HTTPException(status_code=500,detail="Encrypted value fetch error:"+str(e))
            
            if encrypted_value != "Not Found":
                #Decrypt the value 
                try:
                    original_value = tokenisation.decrypt_to_original(encrypted_value,private_key)
                except Exception as e:
                    raise HTTPException(status_code=500,detail="Decrypt to original error: "+str(e))
                
                original_fields[field_name] = original_value
            else:
                original_fields[field_name] = "Not Found"
        
        return {"fields":original_fields}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))