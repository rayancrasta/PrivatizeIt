from sqlalchemy.orm import Session
from sqlalchemy import inspect,MetaData,Table
from models import return_table_object
from typing import List
from schemas import FieldInfo
from database import engine

from sqlalchemy import Column, Integer, String, MetaData, Table

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
    table = Table(domain_name, metadata, *table_columns)

    # Create table in the DB
    table.create(bind=engine)
    
    return "Created",0
    

#Check if table exsists 
def check_table_exsists(db:Session,table_name: str):
    inspector = inspect(db.get_bind())
    
    if inspector.has_table(table_name):
        return True #table exsists
 
    return False 
    


