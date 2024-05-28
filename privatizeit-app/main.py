from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/create-domain-table/",status_code=201)
def create_domain_table(domain_data: schemas.DomainTableCreate,db: Session = Depends(get_db)):
    success = crud.create_domain_table(db,domain_data.domain_name)
    if success:
        msg = "Domain "+domain_data.domain_name+" created succesfully"
        return {'status':'Domain'}
    else:
        raise HTTPException(status_code=400,detail="Domain table already exsists")

    