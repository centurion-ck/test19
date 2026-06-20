from azure.identity import DefaultAzureCredential
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.appcontainers import ContainerAppsAPIClient
from azure.core.exceptions import ResourceNotFoundError

import json
from pathlib import Path


class ResourceDetailAgent:

    def __init__(self, subscription_id):

        self.subscription_id = subscription_id
        credential = DefaultAzureCredential()

        self.web_client = WebSiteManagementClient(
            credential,
            subscription_id
        )

        self.resource_client = ResourceManagementClient(
            credential,
            subscription_id
        )

        self.acr_client = ContainerRegistryManagementClient(
            credential,
            subscription_id
        )

        self.container_client = ContainerAppsAPIClient(
            credential,
            subscription_id
        )

    # -----------------------------
    # Helpers
    # -----------------------------

    def _load_acr_export(self, registry_name: str):
        path = Path(f"exports/acr/{registry_name}.json")
        if not path.exists():
            return {}

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # -----------------------------
    # App Service
    # -----------------------------

    def get_app_service_details(self, resource_group, app_name):

        app = self.web_client.web_apps.get(resource_group, app_name)

        config = self.web_client.web_apps.get_configuration(
            resource_group,
            app_name
        )

        app_settings = self.web_client.web_apps.list_application_settings(
            resource_group,
            app_name
        )
        app_settings_dict = app_settings.properties if app_settings else {}

        conn_strings = self.web_client.web_apps.list_connection_strings(
            resource_group,
            app_name
        )
        connection_strings = conn_strings.properties if conn_strings else {}

        identity = None
        if app.identity:
            identity = {
                "type": app.identity.type,
                "principal_id": app.identity.principal_id
            }

        slots = self.web_client.web_apps.list_slots(resource_group, app_name)
        slot_list = [{"name": slot.name} for slot in slots]

        custom_domains = [
            host
            for host in (app.host_names or [])
            if host and "azurewebsites.net" not in host.lower()
        ]

        return {
            "name": app.name,
            "location": app.location,
            "kind": app.kind,
            "https_only": app.https_only,
            "server_farm_name": (
                app.server_farm_id.split("/")[-1]
                if app.server_farm_id
                else None
            ),
            "default_host_name": app.default_host_name,
            "linux_fx_version": config.linux_fx_version,
            "always_on": config.always_on,
            "ftps_state": config.ftps_state,
            "app_settings": app_settings_dict,
            "connection_strings": connection_strings,
            "identity": identity,
            "deployment_slots": slot_list,
            "custom_domains": custom_domains,
            "certificates": [],
            "vnet_integration": getattr(
                app,
                "virtual_network_subnet_id",
                None
            ),
            "private_endpoints": []
        }

    # -----------------------------
    # Function App
    # -----------------------------

    def get_function_app_details(self, resource_group, function_name):

        app = self.web_client.web_apps.get(resource_group, function_name)

        config = self.web_client.web_apps.get_configuration(
            resource_group,
            function_name
        )

        return {
            "name": app.name,
            "location": app.location,
            "kind": app.kind,
            "https_only": app.https_only,
            "default_host_name": app.default_host_name,
            "linux_fx_version": config.linux_fx_version,
            "always_on": config.always_on,
            "ftps_state": config.ftps_state
        }

    # -----------------------------
    # App Settings
    # -----------------------------

    def get_app_settings(self, resource_group, app_name):
        settings = self.web_client.web_apps.list_application_settings(
            resource_group,
            app_name
        )
        return settings.properties

    def get_connection_strings(self, resource_group, app_name):
        conn = self.web_client.web_apps.list_connection_strings(
            resource_group,
            app_name
        )
        return conn.properties

    # -----------------------------
    # Identity
    # -----------------------------

    def get_managed_identity(self, resource_group, app_name):
        app = self.web_client.web_apps.get(resource_group, app_name)

        if app.identity:
            return {
                "type": app.identity.type,
                "principal_id": app.identity.principal_id
            }

        return {
            "identity": None
        }

    # -----------------------------
    # App Service Plan
    # -----------------------------

    def get_app_service_plan_details(self, resource_group, plan_name):

        plan = self.web_client.app_service_plans.get(
            resource_group,
            plan_name
        )

        return {
            "name": plan.name,
            "location": plan.location,
            "sku_name": plan.sku.name if plan.sku else None,
            "tier": plan.sku.tier if plan.sku else None,
            "capacity": plan.sku.capacity if plan.sku else None,
            "size": plan.sku.size if plan.sku else None,
            "kind": plan.kind,
            "tags": plan.tags or {},
            "is_linux": plan.reserved,
            "maximum_elastic_worker_count": getattr(
                plan,
                "maximum_elastic_worker_count",
                None
            ),
            "zone_redundant": getattr(plan, "zone_redundant", False),
            "per_site_scaling": getattr(plan, "per_site_scaling", None)
        }

    # -----------------------------
    # ACR
    # -----------------------------

    def get_acr_details(self, resource_group, registry_name):

        acr = self.acr_client.registries.get(resource_group, registry_name)
        export = self._load_acr_export(registry_name)

        return {
            "name": acr.name,
            "location": acr.location,
            "sku": export.get(
                "sku",
                acr.sku.name if acr.sku else None
            ),
            "admin_enabled": export.get(
                "admin_enabled",
                acr.admin_user_enabled
            )
        }

    # -----------------------------
    # Container Apps (FINAL FIX APPLIED)
    # -----------------------------

    def get_container_app_details(self, resource_group, app_name):

        try:
            app = self.container_client.container_apps.get(
                resource_group,
                app_name
            )
        except ResourceNotFoundError:
            return {
                "status": "error",
                "message": (
                    f"Container App '{app_name}' not found "
                    f"in resource group '{resource_group}'"
                )
            }

        container = (
            app.template.containers[0]
            if app.template and app.template.containers
            else None
        )

        ingress = (
            app.configuration.ingress
            if app.configuration and app.configuration.ingress
            else None
        )

        scale = getattr(app.template, "scale", None) if app.template else None

        # -----------------------------
        # Env
        # -----------------------------
        env_vars = []
        if container and getattr(container, "env", None):
            env_vars = [
                {"name": e.name, "value": e.value}
                for e in container.env
            ]

        # -----------------------------
        # Registries
        # -----------------------------
        registries = []
        if getattr(app.configuration, "registries", None):
            registries = [
                {"server": r.server}
                for r in app.configuration.registries
            ]

        # -----------------------------
        # Secrets (NO VALUES)
        # -----------------------------
        secrets = []
        if getattr(app.configuration, "secrets", None):
            secrets = [s.name for s in app.configuration.secrets]

        # -----------------------------
        # FIXED Identity Handling
        # -----------------------------
        identity = None
        identity_type = getattr(getattr(app, "identity", None), "type", None)

        if identity_type and identity_type not in ("None", "", "null"):
            identity = identity_type

        # -----------------------------
        # Tags
        # -----------------------------
        tags = getattr(app, "tags", {}) or {}

        return {
            "name": app.name,
            "location": app.location,
            "environment_id": getattr(app, "managed_environment_id", None),

            "ingress": {
                "external": getattr(ingress, "external", None),
                "target_port": getattr(ingress, "target_port", None)
            } if ingress else None,

            "image": container.image if container else None,
            "cpu": (
                container.resources.cpu
                if container and container.resources
                else None
            ),
            "memory": (
                container.resources.memory
                if container and container.resources
                else None
            ),

            "revision_mode": getattr(
                app.configuration,
                "active_revisions_mode",
                None
            ),

            "min_replicas": getattr(scale, "min_replicas", None) if scale else None,
            "max_replicas": getattr(scale, "max_replicas", None) if scale else None,

            "env": env_vars,
            "registries": registries,
            "secrets": secrets,

            "identity": identity,
            "tags": tags
        }