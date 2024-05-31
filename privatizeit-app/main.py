from fastapi import FastAPI, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, crud, tokenisation, database,masking
from crud_mongodb import add_domain_policy,get_tokenisation_policy_id_from_name,get_tokenisation_pname_from_policyid
from typing import List,Dict, Any
from validaton import validate_user_input,fetch_schema
import crud_mongodb

database.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/create-tokenisation-policy/",status_code=201)
async def create_tokenisation_policy(tokenisation_pdata: schemas.DomainTableCreate,db: Session = Depends(get_db)):
    # Create the domain in PostgreSQL
    try:
        msg,exsists = crud.create_domaintable(db, tokenisation_pdata.tokenisation_pname, tokenisation_pdata.fields)
    except Exception as e:
        raise HTTPException(status_code=500, detail="DB"+str(e))

    # print(exsists)
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
    try:
        tokenised_data = await tokenisation.tokenisation_logic(db,user_input)            
        return {"result": tokenised_data}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
      
@app.get("/detokenise-Single-record/",status_code=200)
async def detokenise_single_record(user_input: schemas.UserInputDT = Body(...),db:Session = Depends(get_db)):
    try:
        detokenised_dict = await tokenisation.detokenisation_logic(db,user_input)
        return {"result":detokenised_dict}
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
    
@app.get("/get-masked-record",status_code=200)
async def get_masked_record(masked_req: schemas.MaskedUserIn= Body(...),db:Session = Depends(get_db)):
    masking_policy_id = masked_req.masking_policy_id
    try:
        detokenised_dict = await tokenisation.detokenisation_logic(db,masked_req)
    except Exception as e:
        raise HTTPException(status_code=500,detail="Error detokenising "+str(e))
    
    try:
        masked_dict = await masking.masking_record(detokenised_dict,masking_policy_id)
        return {"result":masked_dict}
    except Exception as e:
        raise HTTPException(status_code=500,detail="Masking error :"+str(e))
    
    
    