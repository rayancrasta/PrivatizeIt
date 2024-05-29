from sqlalchemy.orm import Session
from sqlalchemy import inspect,MetaData,Table
import models
from typing import List
from schemas import FieldInfo
from database import engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Database table generation function
def create_domaintable(db ,domain_name: str, fields: List[FieldInfo]) -> (str,int):
    if check_table_exsists(db,domain_name):
        return "already Exsists",1
    
    metadata = MetaData()

    # Define table dynamically
    table_columns = [Column('id', Integer, primary_key=True)]
    for field in fields:
        if field.field_type == 'numeric':
            column_type = Integer
        else:
            column_type = String(field.field_length)

        table_columns.append(Column(field.field_name, column_type))
    table = Table(domain_name.lower(), metadata, *table_columns)
    # Create table in the DB
    table.create(bind=engine)
    
    #Create the tokenisation counterpart as well
    table_for_data = models.create_or_get_tokenised_data_class(domain_name)
    # Create the table in the database
    Base.metadata.create_all(bind=engine, tables=[table_for_data.__table__])
    
    return "Created",0
    
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
