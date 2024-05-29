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

    #Save the policy in MongoDB
    try:
        if not exsists:
            domain_policy_id = await add_domain_policy(domain_data)
        else:
            domain_policy_id = await get_domain_policy_id_from_name(domain_data.domain_name)
            
         
    except Exception as e:
        raise HTTPException(status_code=500,detail="Mongo"+str(e))
    
    resp_msg = f"Domain {domain_data.domain_name} {msg}"
    return {'status':resp_msg,'domain_policy_id': domain_policy_id}

    
@app.post("/tokenise-Single/", status_code=200)
async def tokenise_single(user_input: schemas.UserInput = Body(...),db: Session = Depends(get_db)):
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
            crud.save_tokenised_data(db,table,original_value,tokenised_value)
                
        return {"result": tokenised_data}
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
    
    