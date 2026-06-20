from fastapi import APIRouter
from agents.acr_dependency_agent import ACRDependencyAgent
from config.settings import SUBSCRIPTION_ID

router = APIRouter()

@router.get(
    "/acr-dependencies/{resource_group}/{registry_name}"
)
def acr_dependencies(
    resource_group: str,
    registry_name: str
):

    agent = ACRDependencyAgent(
        SUBSCRIPTION_ID
    )

    return agent.analyze(
        resource_group,
        registry_name
    )