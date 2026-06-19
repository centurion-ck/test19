from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from database.db import Base


class Resource(Base):

    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    resource_type = Column(String)

    location = Column(String)

    resource_id = Column(String)

    migration_status = Column(String)