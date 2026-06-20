from fastapi import APIRouter
from database.db import SessionLocal
from models.migration_request import MigrationRequest

router = APIRouter()

@router.post("/migration-request")
def create_request():

    db = SessionLocal()

    req = MigrationRequest(
        source_rg="rg-sea-prod",
        destination_rg="rg-eastus-prod",
        destination_region="eastus",
        status="CREATED"
    )

    db.add(req)
    db.commit()

    return {
        "status": "created"
    }

