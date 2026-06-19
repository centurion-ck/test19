from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

class DiscoveryAgent:

    def __init__(self, subscription_id):

        self.client = ResourceManagementClient(
            DefaultAzureCredential(),
            subscription_id
        )

    def scan_resource_group(self, resource_group):

        resources = []

        for resource in self.client.resources.list_by_resource_group(
            resource_group
        ):

            resources.append(
                {
                    "name": resource.name,
                    "type": resource.type,
                    "location": resource.location,
                    "id": resource.id
                }
            )

        return resources