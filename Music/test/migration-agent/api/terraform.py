from fastapi import APIRouter

from database.db import SessionLocal
from models.resource import Resource

from agents.terraform_agent import TerraformAgent

from models.migration_request import (
    TerraformRequest
)

router = APIRouter()


@router.post("/terraform/{resource_id}")
def terraform(
    resource_id: int,
    request: TerraformRequest
):

    db = SessionLocal()

    resource = db.query(
        Resource
    ).filter(
        Resource.id == resource_id
    ).first()

    if not resource:

        return {
            "error": "Resource not found"
        }

    agent = TerraformAgent()

    return agent.generate(
        resource,
        request.destination_region,
        request.destination_resource_group
    )