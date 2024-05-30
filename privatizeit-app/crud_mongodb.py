from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from schemas import DomainTableCreate, MaskingPolicyCreate
from mongodb import tokenisation_policy_collection,domain_helper,masking_policy_colleciton

async def add_domain_policy(tokenisation_pdata: DomainTableCreate) -> int:
    try:
        existing_policy = await masking_policy_colleciton.find_one({"domain_name": tokenisation_pdata.tokenisation_pname})
        if existing_policy:
                return str(existing_policy["_id"])
            
        domain_dict = tokenisation_pdata.model_dump() #create a dictionary from the data
        newdomain = await tokenisation_policy_collection.insert_one(domain_dict)
        getdomain = await tokenisation_policy_collection.find_one({"_id": newdomain.inserted_id})
        # print("ID created: ",newdomain)
        # domaindict =  domain_helper(getdomain)
        return str(newdomain.inserted_id)
    except Exception as e:
        raise e 

async def get_tokenisation_policy_id_from_name(tokenisation_pname: str) -> str:
    try:
        getdomain = await tokenisation_policy_collection.find_one({"tokenisation_pname": tokenisation_pname})
        domaindict =  domain_helper(getdomain)
        print("Domain dict: ",domaindict['id'])
        return domaindict['id']
    except Exception as e:
        return "Cant find policy ID"
    
async def get_tokenisation_pname_from_policyid(domain_policyid: str):
    try:
        getdomain = await tokenisation_policy_collection.find_one({"_id": ObjectId(domain_policyid)})
        domaindict =  domain_helper(getdomain)
        return domaindict['tokenisation_pname']
    except Exception as e:
        raise Exception("Cant find policy")
    
async def save_masking_policy(masking_rules: MaskingPolicyCreate) -> str:
    try:
        existing_policy = await masking_policy_colleciton.find_one({"domain_name": masking_rules.domain_name})
        if existing_policy:
            return str(existing_policy["_id"])
        
        masking_rulesdict = masking_rules.model_dump()
        newdomain = await masking_policy_colleciton.insert_one(masking_rulesdict)
        return str(newdomain.inserted_id)
    except Exception as e:
        raise e 
    
    
    
    