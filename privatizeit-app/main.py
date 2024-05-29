from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, crud
from crud_mongodb import add_domain_policy,get_domain_policy_id
models.Base.metadata.create_all(bind=engine)

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
            domain_policy_id = await get_domain_policy_id(domain_data.domain_name)
            
         
    except Exception as e:
        raise HTTPException(status_code=500,detail="Mongo"+str(e))
    
    resp_msg = f"Domain {domain_data.domain_name} {msg}"
    return {'status':resp_msg,'domain_policy_id': domain_policy_id}

    
    