from fastapi import APIRouter

from agents.resource_detail_agent import ResourceDetailAgent
from config.settings import SUBSCRIPTION_ID

router = APIRouter()


@router.get(
    "/resource-details/appservice/{resource_group}/{app_name}"
)
def get_appservice_details(
    resource_group: str,
    app_name: str
):

    agent = ResourceDetailAgent(
        SUBSCRIPTION_ID
    )

    return agent.get_app_service_details(
        resource_group,
        app_name
    )


@router.get(
    "/resource-details/appserviceplan/{resource_group}/{plan_name}"
)
def get_appservice_plan_details(
    resource_group: str,
    plan_name: str
):

    agent = ResourceDetailAgent(
        SUBSCRIPTION_ID
    )

    return agent.get_app_service_plan_details(
        resource_group,
        plan_name
    )


@router.get(
    "/resource-details/acr/{resource_group}/{registry_name}"
)
def get_acr_details(
    resource_group: str,
    registry_name: str
):

    agent = ResourceDetailAgent(
        SUBSCRIPTION_ID
    )

    return agent.get_acr_details(
        resource_group,
        registry_name
    )


@router.get(
    "/resource-details/containerapp/{resource_group}/{app_name}"
)
def get_container_app_details(
    resource_group: str,
    app_name: str
):

    agent = ResourceDetailAgent(
        SUBSCRIPTION_ID
    )

    return agent.get_container_app_details(
        resource_group,
        app_name
    )


@router.get(
    "/resource-details/appsettings/{resource_group}/{app_name}"
)
def get_app_settings(
    resource_group: str,
    app_name: str
):

    agent = ResourceDetailAgent(
        SUBSCRIPTION_ID
    )

    return agent.get_app_settings(
        resource_group,
        app_name
    )

@router.get(
    "/resource-details/connectionstrings/{resource_group}/{app_name}"
)
def get_connection_strings(
    resource_group: str,
    app_name: str
):

    agent = ResourceDetailAgent(
        SUBSCRIPTION_ID
    )

    return agent.get_connection_strings(
        resource_group,
        app_name
    )