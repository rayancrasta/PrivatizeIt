from typing import List,Any, Dict
from pydantic import BaseModel, Field


class FieldInfo(BaseModel):
    field_name: str
    field_type: str  # Options: 'numeric', 'char', 'alphanumeric'
    field_length: int

class DomainTableCreate(BaseModel):
    tokenisation_pname: str
    domain_name: str
    key_pass: str
    fields: List[FieldInfo]
    
class MaskingRuleInfo(BaseModel):
    field_name: str
    show_start: int
    show_last: int    

class MaskingPolicyCreate(BaseModel):
    domain_name: str
    masking_policy_name: str
    tokenisation_policy_id: str
    rules: List[MaskingRuleInfo]
    
class TokenisationPolicy(BaseModel):
    id: str
    tokenisation_pname: str
    domain_name: str
    fields : List[FieldInfo]
    
    class Config:
        orm_mode = True
        
# TOKENISATION input
class UserInputT(BaseModel):
    tokenisation_policy_id: str
    domain_key : str
    fields: Dict[str, Any]

# DEtokenisationInput
class UserInputDT(BaseModel):
    tokenisation_policy_id: str
    key_pass : str
    fields: Dict[str, Any]

#Keys mapped to domains
class KeysToDomains(BaseModel):
    tokenisation_policy_id: str
    private_key: str
    
#Masked data request input
class MaskedUserIn(BaseModel):
    tokenisation_policy_id: str
    masking_policy_id : str
    key_pass : str
    fields: Dict[str, Any]
    