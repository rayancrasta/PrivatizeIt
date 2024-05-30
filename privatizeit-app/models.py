from sqlalchemy import Column,Table, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
import database
from database import Base

def create_or_get_tokenised_data_class(domain_name:str) -> Table:
    metadata = MetaData()

    # Check if table already exists
    if domain_name.lower() + '_tokenised_data' in metadata.tables:
        return metadata.tables[domain_name.lower() + '_tokenised_data']
    
    # Table doesn't exist, define it and add it to metadata
    table = Table(
        domain_name.lower() + '_tokenised_data',
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('original_value', String),
        Column('tokenised_value', String)
    )

    # Create the table in the database
    metadata.create_all(bind=database.engine)
    
    return table

class KeysToDomainModel(Base):
    __tablename__ = 'domainkeys'
    
    id = Column(Integer, primary_key=True, index=True)
    tokenisation_policy_id = Column(String, unique=True, index=True)
    domain_name = Column(String, unique=True)
    private_key = Column(String, nullable=False)
    
    