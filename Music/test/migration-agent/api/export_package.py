from fastapi import APIRouter

from agents.export_package_agent import ExportPackageAgent

router = APIRouter()


@router.get(
    "/export-package/{resource_group}"
)
def export_package(
    resource_group: str
):

    agent = ExportPackageAgent()

    return agent.export(
        resource_group
    )