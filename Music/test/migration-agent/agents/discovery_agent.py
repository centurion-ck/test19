from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

from database.db import SessionLocal
from models.resource import Resource


class DiscoveryAgent:

    def __init__(self, subscription_id):

        self.client = ResourceManagementClient(
            DefaultAzureCredential(),
            subscription_id
        )

    def scan_resource_group(self, resource_group):

        inventory = []

        db = SessionLocal()

        try:
            resources = self.client.resources.list_by_resource_group(
                resource_group
            )

            for resource in resources:

                inventory.append(
                    {
                        "name": resource.name,
                        "type": resource.type,
                        "location": resource.location,
                        "id": resource.id
                    }
                )

                # ✅ SAFE INSERT (deduplication logic added)
                existing = db.query(Resource).filter(
                    Resource.resource_id == resource.id
                ).first()

                if not existing:

                    db_resource = Resource(
                        name=resource.name,
                        resource_type=resource.type,
                        location=resource.location,
                        resource_id=resource.id,
                        migration_status="DISCOVERED"
                    )

                    db.add(db_resource)

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        return inventory