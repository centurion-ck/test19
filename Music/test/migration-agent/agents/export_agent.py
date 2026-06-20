import os
import json


class ExportAgent:

    def export_resource(
        self,
        resource_type,
        resource_name,
        data
    ):

        folder = f"exports/{resource_type}"

        os.makedirs(
            folder,
            exist_ok=True
        )

        filename = f"{folder}/{resource_name}.json"

        with open(
            filename,
            "w"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )

        return {
            "status": "exported",
            "file": filename
        }