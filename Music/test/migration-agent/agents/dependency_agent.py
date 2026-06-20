from database.db import SessionLocal
from models.resource import Resource


class DependencyAgent:

    def analyze(self, resource):

        dependencies = []

        # App Service dependencies
        if "Microsoft.Web/sites" in resource.resource_type:

            dependencies.append("Microsoft.Web/serverFarms")
            dependencies.append("microsoft.insights/components")
            dependencies.append("Microsoft.Storage/storageAccounts")

        # Container Apps dependencies
        elif "Microsoft.App/containerApps" in resource.resource_type:

            dependencies.append("Microsoft.App/managedEnvironments")
            dependencies.append("Microsoft.ContainerRegistry/registries")

        # Container Registry dependencies
        elif "Microsoft.ContainerRegistry/registries" in resource.resource_type:

            dependencies.append({
                "dependency_type": "PrivateEndpoint",
                "status": "CHECK_REQUIRED"
            })

            dependencies.append({
                "dependency_type": "ManagedIdentity",
                "status": "CHECK_REQUIRED"
            })

            dependencies.append({
                "dependency_type": "NetworkRules",
                "status": "CHECK_REQUIRED"
            })

            dependencies.append({
                "dependency_type": "Replication",
                "status": "CHECK_REQUIRED"
            })

        return {
            "resource_name": resource.name,
            "resource_type": resource.resource_type,
            "dependencies": dependencies
        }