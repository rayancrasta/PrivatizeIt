from pydantic import BaseModel

class DomainTableCreate(BaseModel):
    domain_name: str
    