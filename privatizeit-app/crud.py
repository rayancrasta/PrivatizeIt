from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy import inspect,MetaData,Table
import models
from typing import List
from schemas import FieldInfo
from database import engine,get_db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Database table generation function
def create_domaintable(db ,tokenisation_pname: str, fields: List[FieldInfo]):
    if check_table_exsists(db,tokenisation_pname):
        return "already Exsists",True

    metadata = MetaData()

    # Define table dynamically
    table_columns = [Column('id', Integer, primary_key=True)]
    for field in fields:
        if field.field_type == 'numeric':
            column_type = Integer
        else:
            column_type = String(field.field_length)

        table_columns.append(Column(field.field_name, column_type))
    table = Table(tokenisation_pname.lower(), metadata, *table_columns)
    # Create the table in the database
    Base.metadata.create_all(bind=engine,tables=[table])
    
    #Create the table that stores the tokenised data as well counterpart as well
    models.create_or_get_tokenised_data_class(tokenisation_pname)

    return "Created",False
    
#Check if table exsists 
def check_table_exsists(db:Session,table_name: str):
    inspector = inspect(db.get_bind())
    
    if inspector.has_table(table_name.lower()):
        return True #table exsists
 
    return False 
    
#Save the tokenised value in the database
def save_tokenised_data(db:Session,table: Table,original_value:str,tokenised_value:str):
    try:
        # Create a new record
        db.execute(
            table.insert().values(
                original_value=original_value,
                tokenised_value=tokenised_value
            )
        )
        db.commit()
        
        # return db_data
    except Exception as e:
        print("Saving tokenised data exception: ",e)

#Get mapping of original value
def get_encrypted_value(db:Session,table: Table,tokenised_value:str) -> str:
    original_record = db.query(table).filter(table.c.tokenised_value == tokenised_value).first()
    
    if original_record:
        return original_record.original_value
    else:
        return "Not Found"
    
#Store private key for a domain in DB
def store_privatekey(db:Session,tokenisation_policy_id,tokenisation_pname,private_key):
    try:
        db_data = models.KeysToDomainModel(
            tokenisation_policy_id=tokenisation_policy_id,
            tokenisation_pname = tokenisation_pname,
            private_key=private_key
        )   
        db.add(db_data)
        db.commit()
        db.refresh(db_data)
    except Exception as e:
        raise ValueError("Error saving private key"+ str(e))    

#Get private key for a specific policy id
def get_private_key(tokenisation_policy_id :str,db: Session = Depends(get_db)) -> str:
    try:
        record = db.query(models.KeysToDomainModel).filter(models.KeysToDomainModel.tokenisation_policy_id== tokenisation_policy_id).first()
        
        if record:
            return record.private_key
        else:
            raise ValueError("No key for the tokenisation_policy_id")
    except Exception as e:
        raise ValueError(f"Error fetching private key: {e}")