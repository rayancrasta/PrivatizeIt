from typing import List,Any, Dict
from pydantic import BaseModel, Field


class FieldInfo(BaseModel):
    field_name: str
    field_type: str  # Options: 'numeric', 'char', 'alphanumeric'
    field_length: int

class DomainTableCreate(BaseModel):
    domain_name: str
    fields: List[FieldInfo]
    
class DomainPolicy(BaseModel):
    id: str
    domain_name: str
    fields : List[FieldInfo]
    
    class Config:
        orm_mode = True
        
# TOKENISATION input
class UserInputT(BaseModel):
    domain_policy_id: str
    domain_key : str
    fields: Dict[str, Any]

# DEtokenisationInput
class UserInputDT(BaseModel):
    domain_policy_id: str
    fields: Dict[str, Any]

#Keys mapped to domains
class KeysToDomains(BaseModel):
    domain_policy_id: str
    private_key: str