from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from database.db import SessionLocal
from models.resource import Resource

db = SessionLocal()

for resource in resources:

    db_resource = Resource(

        name=resource.name,

        resource_type=resource.type,

        location=resource.location,

        resource_id=resource.id,

        migration_status="DISCOVERED"
    )

    db.add(db_resource)

db.commit()

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