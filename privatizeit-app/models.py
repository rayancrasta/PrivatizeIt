from sqlalchemy import Column,Integer,String, MetaData, Table
from database import Base

def return_table_object(domain_name: str):
    metadata = MetaData()
    
    return Table (
        domain_name + "_data",
        metadata,
        Column("id",Integer,primary_key=True,index=True),
        Column("original_data",String),
        Column("tokenised_data",String),
    )
    

    