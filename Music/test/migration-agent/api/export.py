from fastapi import APIRouter

from agents.resource_detail_agent import ResourceDetailAgent
from agents.export_agent import ExportAgent

from config.settings import SUBSCRIPTION_ID
from agents.acr_dependency_agent import ACRDependencyAgent

router = APIRouter()


@router.get(
    "/export/appservice/{resource_group}/{app_name}"
)
def export_appservice(
    resource_group: str,
    app_name: str
):

    detail_agent = ResourceDetailAgent(
        SUBSCRIPTION_ID
    )

    data = detail_agent.get_app_service_details(
        resource_group,
        app_name
    )

    export_agent = ExportAgent()

    return export_agent.export_resource(
        "appservice",
        app_name,
        data
    )

@router.get(
    "/export/acr/{resource_group}/{registry_name}"
)
def export_acr(
    resource_group: str,
    registry_name: str
):

    acr_agent = ACRDependencyAgent(
        SUBSCRIPTION_ID
    )

    data = acr_agent.analyze(
        resource_group,
        registry_name
    )

    export_agent = ExportAgent()

    return export_agent.export_resource(
        "acr",
        registry_name,
        data
    )

@router.get(
    "/export/containerapp/{resource_group}/{app_name}"
)
def export_containerapp(
    resource_group: str,
    app_name: str
):

    detail_agent = ResourceDetailAgent(
        SUBSCRIPTION_ID
    )

    data = detail_agent.get_container_app_details(
        resource_group,
        app_name
    )

    export_agent = ExportAgent()

    return export_agent.export_resource(
        "containerapp",
        app_name,
        data
    )