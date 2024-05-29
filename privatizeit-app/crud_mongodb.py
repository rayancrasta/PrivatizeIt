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
    try:
        getdomain = await domain_collection.find_one({"domain_name": domain_name})
        domaindict =  domain_helper(getdomain)
        return domaindict['id']
    except Exception as e:
        return "Cant find policy ID"
    
async def get_domain_name_from_policyid(domain_policyid: str):
    try:
        getdomain = await domain_collection.find_one({"_id": ObjectId(domain_policyid)})
        domaindict =  domain_helper(getdomain)
        return domaindict['domain_name']
    except Exception as e:
        raise Exception("Cant find policy")