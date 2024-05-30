from typing import Dict, List, Any
from pydantic import BaseModel, create_model, ValidationError
from schemas import DomainPolicy, FieldInfo
from crud_mongodb import domain_collection
from bson import ObjectId
from fastapi import HTTPException

# Fetch the domain policy using the domain policy id
async def fetch_schema(tokenisation_policy_id: str) -> DomainPolicy:
    document = await domain_collection.find_one({"_id": ObjectId(tokenisation_policy_id)})
    # print("Document from mongo: ", document)
    if document:
        # Map _id to id
        document["id"] = str(document["_id"])
        del document["_id"]
        return DomainPolicy(**document)
    else:
        raise HTTPException(status_code=404, detail="Schema not found")

# Validate if the user input is same as the schema expected from the policy
async def validate_user_input(tokenisation_policy_id: str, schema, user_input: Dict[str, Any]) -> bool:
    # Create a dynamic Pydantic model
    field_definitions = {}
    for field in schema.fields:
        field_type = str if field.field_type in ['char', 'alphanumeric'] else int
        field_definitions[field.field_name] = (field_type, ...)
    # print(field_definitions)
    DynamicModel = create_model('DynamicModel', **field_definitions)

    # Validate user input
    try:
        data = DynamicModel(**user_input)
        # print(data)
        return True
    except ValidationError as e:
        print(e)
        return False
