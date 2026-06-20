from fastapi import APIRouter

from database.db import SessionLocal
from models.resource import Resource

from agents.dependency_agent import DependencyAgent

router = APIRouter()


@router.get("/dependencies/{resource_id}")
def dependencies(resource_id: int):

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

    agent = DependencyAgent()

    return agent.analyze(
        resource
    )