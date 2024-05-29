from typing import List,Any, Dict
from pydantic import BaseModel, Field


class FieldInfo(BaseModel):
    field_name: str
    field_type: str  # Options: 'numeric', 'char', 'alphanumeric'
    field_length: int

class DomainTableCreate(BaseModel):
    domain_name: str
    fields: List[FieldInfo]

class DataToTokenise(BaseModel):
    domain_policy_id : str
    original_data: str
    
class DomainPolicy(BaseModel):
    id: str
    domain_name: str
    fields : List[FieldInfo]
    
    class Config:
        orm_mode = True
        
# Pydantic model for user input
class UserInput(BaseModel):
    domain_policy_id: str
    fields: Dict[str, Any]