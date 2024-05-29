from motor.motor_asyncio import AsyncIOMotorClient
from schemas import DomainPolicy

MONGO_DETAILS="mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)

database = client['privatizeit']

domain_collection = database.get_collection("domain_policies")

# Use the Pydantic model for the helper function
def domain_helper(domain) -> dict:
    print("Mongocode: ",domain)
    return DomainPolicy(
        id=str(domain["_id"]),
        domain_name=domain["domain_name"],
        fields=domain["fields"]
    ).model_dump()
    
    