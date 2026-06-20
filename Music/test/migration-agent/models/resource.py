from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from database.db import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    resource_type = Column(String)

    location = Column(String)

    resource_id = Column(String, unique=True)

    migration_status = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )