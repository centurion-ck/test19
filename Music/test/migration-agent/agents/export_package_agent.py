import os
import json

from database.db import SessionLocal
from models.resource import Resource


class ExportPackageAgent:

    def export(self, resource_group):

        db = SessionLocal()

        resources = db.query(
            Resource
        ).all()

        export_path = f"exports/{resource_group}"

        os.makedirs(
            export_path,
            exist_ok=True
        )

        inventory = []

        for resource in resources:

            inventory.append(
                {
                    "id": resource.id,
                    "name": resource.name,
                    "type": resource.resource_type,
                    "location": resource.location
                }
            )

        with open(
            f"{export_path}/inventory.json",
            "w"
        ) as f:

            json.dump(
                inventory,
                f,
                indent=4
            )

        return {
            "status": "exported",
            "resource_count": len(inventory),
            "path": export_path
        }