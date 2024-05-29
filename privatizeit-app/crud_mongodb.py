from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from schemas import DomainTableCreate
from mongodb import domain_collection,domain_helper

async def add_domain_policy(domain_data: DomainTableCreate) -> int:
    domain_dict = domain_data.model_dump() #create a dictionary from the data
     
    newdomain = await domain_collection.insert_one(domain_dict)
    
    
    getdomain = await domain_collection.find_one({"_id": newdomain.inserted_id})
    # print("ID created: ",newdomain)
    domaindict =  domain_helper(getdomain)
    return domaindict['id']

async def get_domain_policy_id_from_name(domain_name: str) -> str:
    getdomain = await domain_collection.find_one({"domain_name": domain_name})
    try:
        domaindict =  domain_helper(getdomain)
        return domaindict['id']
    except Exception as e:
        return "Cant find policy ID"
    
