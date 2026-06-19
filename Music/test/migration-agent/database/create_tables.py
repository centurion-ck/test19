from database.db import Base
from database.db import engine

from models.resource import Resource

Base.metadata.create_all(
    bind=engine
)

print("Tables Created")