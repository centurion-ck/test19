from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from database.db import Base


MIGRATION_STATUSES = [
    "DISCOVERED",
    "PLANNED",
    "EXPORTED",
    "TERRAFORM_GENERATED",
    "DEPLOYED",
    "VALIDATED",
    "CUTOVER_COMPLETE",
    "FAILED",
    "ROLLED_BACK"
]


class Migration(Base):
    __tablename__ = "migrations"

    id = Column(Integer, primary_key=True)

    resource_name = Column(String)
    resource_type = Column(String)

    source_region = Column(String)
    target_region = Column(String)

    status = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )