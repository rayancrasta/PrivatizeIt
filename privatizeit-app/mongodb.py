from motor.motor_asyncio import AsyncIOMotorClient
from schemas import TokenisationPolicy

MONGO_DETAILS="mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)

database = client['privatizeit']

tokenisation_policy_collection = database.get_collection("tokenisation_policies")
masking_policy_colleciton = database.get_collection("masking_policies")

# Use the Pydantic model for the helper function
def domain_helper(domain) -> dict:
    print("Mongocode: ",domain)
    return TokenisationPolicy(
        id=str(domain["_id"]),
        tokenisation_pname=domain["tokenisation_pname"],
        domain_name=domain["domain_name"],
        fields=domain["fields"]
    ).model_dump()
    
    