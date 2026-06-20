from enum import Enum

from fastapi import APIRouter, HTTPException

from database.db import SessionLocal

from models.resource import Resource
from models.migration import Migration

from agents.planner_agent import PlannerAgent

router = APIRouter()


class MigrationStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    PLANNED = "PLANNED"
    EXPORTED = "EXPORTED"
    TERRAFORM_GENERATED = "TERRAFORM_GENERATED"
    DEPLOYED = "DEPLOYED"
    VALIDATED = "VALIDATED"
    CUTOVER_COMPLETE = "CUTOVER_COMPLETE"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


@router.get("/plans")
def get_plans():
    db = SessionLocal()
    try:
        plans = db.query(Migration).all()
        return plans
    finally:
        db.close()


@router.post("/generate-plan/{resource_id}")
def generate_plan(resource_id: int):
    db = SessionLocal()

    try:
        # Fetch resource
        resource = db.query(Resource).filter(Resource.id == resource_id).first()

        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        # Generate plan
        planner = PlannerAgent()
        plan = planner.create_plan(resource, "eastus", "rg-eastus-prod")

        # Save migration plan
        migration = Migration(
            resource_name=plan["resource_name"],
            resource_type=plan["resource_type"],
            source_region=plan["source_region"],
            target_region=plan["target_region"],
            status=MigrationStatus.PLANNED.value
        )

        db.add(migration)
        db.commit()
        db.refresh(migration)

        # Return stored result (safer than raw plan)
        return {
            "id": migration.id,
            "resource_name": migration.resource_name,
            "resource_type": migration.resource_type,
            "source_region": migration.source_region,
            "target_region": migration.target_region,
            "status": migration.status
        }

    finally:
        db.close()