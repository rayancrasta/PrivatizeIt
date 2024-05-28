from sqlalchemy.orm import Session
from sqlalchemy import inspect
from models import return_table_object

def create_domain_table(db: Session, domain_name: str) -> bool:
    table_name = domain_name + "_data"
    inspector = inspect(db.bind)  # Create an inspector from the database connection
    if not inspector.has_table(table_name):  # Check if table exists
        domain_table = return_table_object(domain_name)  # Returns a Table object and its properties
        domain_table.create(db.bind)  # Create the table using the object
        return True
    else:
        return False
