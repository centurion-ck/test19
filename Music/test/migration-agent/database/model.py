from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Resource(Base):

    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    resource_type = Column(String)

    location = Column(String)

    resource_id = Column(String)