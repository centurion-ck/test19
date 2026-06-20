from database.db import Base
from database.db import engine

from models.resource import Resource
from models.migration import Migration
from models.migration_request import MigrationRequest

Base.metadata.create_all(bind=engine)

print("Tables Created")