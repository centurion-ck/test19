from typing import Optional, Dict, Any, List

from azure.identity import DefaultAzureCredential
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.core.exceptions import HttpResponseError


class ACRDependencyAgent:
    """
    Agent responsible for fetching Azure Container Registry metadata,
    replications, and dependency-aware analysis.
    """

    def __init__(
        self,
        subscription_id: str,
        credential: Optional[DefaultAzureCredential] = None
    ):
        self.subscription_id = subscription_id
        self.credential = credential or DefaultAzureCredential()

        self.client = ContainerRegistryManagementClient(
            credential=self.credential,
            subscription_id=self.subscription_id
        )

    # -----------------------------
    # Registry Fetch
    # -----------------------------
    def get_registry(
        self,
        resource_group: str,
        registry_name: str
    ) -> Dict[str, Any]:

        try:
            registry = self.client.registries.get(
                resource_group,
                registry_name
            )

            network_rules = None

            if hasattr(registry, "network_rule_set"):
                network_rules = registry.network_rule_set

            return {
                "id": registry.id,
                "name": registry.name,
                "location": registry.location,
                "sku": registry.sku.name if registry.sku else None,
                "login_server": registry.login_server,
                "admin_user_enabled": registry.admin_user_enabled,
                "identity": (
                    {
                        "type": registry.identity.type
                    }
                    if registry.identity
                    else None
                ),
                "tags": registry.tags or {},
                "network_rules": (
                    str(network_rules)
                    if network_rules
                    else None
                ),
                "public_network_access": getattr(
                    registry,
                    "public_network_access",
                    None
                ),
                "encryption": (
                    {
                        "status": registry.encryption.status
                    }
                    if getattr(registry, "encryption", None)
                    else None
                )
            }

        except HttpResponseError as e:
            raise RuntimeError(
                f"Failed to fetch ACR registry '{registry_name}' "
                f"in resource group '{resource_group}': {e}"
            ) from e

    # -----------------------------
    # Replications
    # -----------------------------
    def get_replications(
        self,
        resource_group: str,
        registry_name: str
    ) -> List[Dict[str, Any]]:

        try:
            replications = self.client.replications.list(
                resource_group,
                registry_name
            )

            return [
                {
                    "name": r.name,
                    "location": r.location
                }
                for r in replications
            ]

        except HttpResponseError as e:
            raise RuntimeError(
                f"Failed to fetch replications for '{registry_name}': {e}"
            ) from e

    # -----------------------------
    # Private Endpoints
    # -----------------------------
    def get_private_endpoints(
        self,
        resource_group: str,
        registry_name: str
    ) -> List[Dict[str, Any]]:

        try:
            pe_connections = (
                self.client.private_endpoint_connections.list(
                    resource_group,
                    registry_name
                )
            )

            return [
                {
                    "name": pe.name,
                    "id": pe.id
                }
                for pe in pe_connections
            ]

        except Exception:
            return []

    # -----------------------------
    # Existence Check
    # -----------------------------
    def registry_exists(
        self,
        resource_group: str,
        registry_name: str
    ) -> bool:

        try:
            self.client.registries.get(
                resource_group,
                registry_name
            )
            return True

        except HttpResponseError:
            return False

    # -----------------------------
    # Production Analyzer
    # -----------------------------
    def analyze(
        self,
        resource_group: str,
        registry_name: str
    ) -> Dict[str, Any]:

        registry = self.get_registry(
            resource_group,
            registry_name
        )

        return {
            "resource_type": "Microsoft.ContainerRegistry/registries",
            "resource_name": registry_name,
            "configuration": registry,
            "replications": self.get_replications(
                resource_group,
                registry_name
            ),
            "private_endpoints": self.get_private_endpoints(
                resource_group,
                registry_name
            )
        }