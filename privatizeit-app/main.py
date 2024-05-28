from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/create-domain-table/",status_code=201)
def create_domain_table(domain_data: schemas.DomainTableCreate,db: Session = Depends(get_db)):
    msg = crud.create_domaintable(db,domain_data.domain_name,domain_data.fields)
    
    resp_msg = "Domain "+domain_data.domain_name+" "+msg
    return {'status':resp_msg} 



    