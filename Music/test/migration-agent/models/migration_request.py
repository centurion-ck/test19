from sqlalchemy import Column, Integer, String
from database.db import Base
from pydantic import BaseModel

class MigrationRequest(Base):

    __tablename__ = "migration_requests"

    id = Column(Integer, primary_key=True)

    source_rg = Column(String)

    destination_rg = Column(String)

    destination_region = Column(String)

    status = Column(String)
    

class TerraformRequest(BaseModel):

    destination_region: str

    destination_resource_group: str