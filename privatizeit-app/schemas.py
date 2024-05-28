from typing import List
from pydantic import BaseModel, Field


class FieldInfo(BaseModel):
    field_name: str
    field_type: str  # Options: 'numeric', 'char', 'alphanumeric'
    field_length: int

class DomainTableCreate(BaseModel):
    domain_name: str
    fields: List[FieldInfo]

class DataToTokenise(BaseModel):
    domain_name: str
    original_data: str
    domain_key : str
    
    