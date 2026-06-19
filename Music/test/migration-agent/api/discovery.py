from fastapi import APIRouter

from agents.discovery_agent import DiscoveryAgent
from config.settings import SUBSCRIPTION_ID

from database.db import SessionLocal
from models.resource import Resource

router = APIRouter()


@router.get("/scan/{resource_group}")
def scan(resource_group: str):

    agent = DiscoveryAgent(
        SUBSCRIPTION_ID
    )

    inventory = agent.scan_resource_group(
        resource_group
    )

    return {
        "resource_group": resource_group,
        "resources": inventory
    }


@router.get("/inventory")
def inventory():

    db = SessionLocal()

    resources = db.query(
        Resource
    ).all()

    return resources