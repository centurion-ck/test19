import os
import json


class TerraformAgent:

    def _tf_name(self, name: str) -> str:
        """
        Converts Azure resource name into a Terraform-safe identifier.
        """
        return name.replace("-", "_").replace(".", "_")

    def _generate_provider_file(self):
        provider_file = "terraform/generated/provider.tf"

        if os.path.exists(provider_file):
            return

        provider_code = '''
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.78"
    }
  }
}

provider "azurerm" {
  features {}
}
'''

        with open(provider_file, "w") as f:
            f.write(provider_code)

    def generate(self, resource, destination_region, destination_rg):

        os.makedirs(
            "terraform/generated",
            exist_ok=True
        )

        self._generate_provider_file()

        resource_type = getattr(resource, "resource_type", "")
        resource_name = getattr(resource, "name", None)

        if not resource_name:
            return {
                "status": "error",
                "message": "Resource name is missing"
            }

        terraform_name = self._tf_name(resource_name)

        tf_code = None

        # -------------------------------
        # Container Registry (ACR)
        # -------------------------------
        if "Microsoft.ContainerRegistry" in resource_type:

            acr_export_file = f"exports/acr/{resource_name}.json"

            if not os.path.exists(acr_export_file):
                return {"status": "error", "message": f"Missing {acr_export_file}"}

            try:
                with open(acr_export_file) as f:
                    acr_details = json.load(f)
            except Exception as e:
                return {"status": "error", "message": str(e)}

            config = acr_details.get("configuration", {})
            sku = config.get("sku", "Basic")
            admin_enabled = config.get("admin_user_enabled", False)

            tf_code = f'''
resource "azurerm_container_registry" "{terraform_name}" {{
  name                = "{resource_name}"
  location            = "{destination_region}"
  resource_group_name = "{destination_rg}"

  sku           = "{sku}"
  admin_enabled = {str(admin_enabled).lower()}
}}
'''

        # -------------------------------
        # App Service Plan
        # -------------------------------
        elif "Microsoft.Web/serverFarms" in resource_type:

            tf_code = f'''
resource "azurerm_service_plan" "{terraform_name}" {{
  name                = "{resource_name}"
  location            = "{destination_region}"
  resource_group_name = "{destination_rg}"

  os_type  = "Linux"
  sku_name = "B1"
}}
'''

        # -------------------------------
        # Web App
        # -------------------------------
        elif "Microsoft.Web/sites" in resource_type:

            app_export_file = f"exports/appservice/{resource_name}.json"

            if not os.path.exists(app_export_file):
                return {"status": "error", "message": f"Missing {app_export_file}"}

            try:
                with open(app_export_file) as f:
                    app_details = json.load(f)
            except Exception as e:
                return {"status": "error", "message": str(e)}

            server_farm_name = app_details.get("server_farm_name")
            if not server_farm_name:
                return {"status": "error", "message": "Missing server_farm_name"}

            terraform_plan_name = self._tf_name(server_farm_name)

            linux_fx_version = app_details.get("linux_fx_version", "")
            python_version = (
                linux_fx_version.split("|")[1]
                if "PYTHON|" in linux_fx_version
                else "3.8"
            )

            tf_code = f'''
resource "azurerm_linux_web_app" "{terraform_name}" {{
  name                = "{resource_name}"
  location            = "{destination_region}"
  resource_group_name = "{destination_rg}"

  service_plan_id = azurerm_service_plan.{terraform_plan_name}.id

  site_config {{
    always_on  = {str(app_details.get("always_on", False)).lower()}
    ftps_state = "{app_details.get("ftps_state", "Disabled")}"

    application_stack {{
      python_version = "{python_version}"
    }}
  }}
}}
'''

        # -------------------------------
        # Container Apps
        # -------------------------------
        elif "Microsoft.App/containerApps" in resource_type:

            export_file = f"exports/containerapp/{resource_name}.json"

            if not os.path.exists(export_file):
                return {"status": "error", "message": f"Missing {export_file}"}

            try:
                with open(export_file) as f:
                    app = json.load(f)
            except Exception as e:
                return {"status": "error", "message": str(e)}

            image = app.get("image")
            environment_id = app.get("environment_id")

            if not image or not environment_id:
                return {"status": "error", "message": "Missing image or environment_id"}

            cpu = app.get("cpu", 0.5)
            memory = app.get("memory", "1Gi")
            revision_mode = app.get("revision_mode", "Single")

            registries = app.get("registries", [])
            ingress = app.get("ingress", {})
            identity = app.get("identity")
            env_vars = app.get("env", [])
            secrets = app.get("secrets", [])

            registry_block = ""
            for r in registries:
                server = r.get("server")
                reg_identity = r.get("identity")

                if not server:
                    continue

                if reg_identity and str(reg_identity).strip():
                    registry_block += f'''
  registry {{
    server   = "{server}"
    identity = "{reg_identity}"
  }}
'''
                else:
                    registry_block += f'''
  registry {{
    server = "{server}"
  }}
'''

            ingress_block = ""
            if ingress:
                ingress_block = f'''
  ingress {{
    external_enabled = {str(ingress.get("external", False)).lower()}
    target_port      = {ingress.get("target_port", 80)}
  }}
'''

            identity_block = ""
            if identity:
                identity_type = identity.get("type") if isinstance(identity, dict) else identity

                if identity_type:
                    identity_block = f'''
  identity {{
    type = "{identity_type}"
  }}
'''

            secret_block = ""
            for s in secrets:
                secret_block += f'''
  secret {{
    name  = "{s}"
    value = var.{s.replace("-", "_")}
  }}
'''

            env_block = ""
            for e in env_vars:
                env_block += f'''
        env {{
          name  = "{e.get("name")}"
          value = "{e.get("value")}"
        }}
'''

            env_name = environment_id.split("/")[-1]
            terraform_env_name = self._tf_name(env_name)

            tf_code = f'''
resource "azurerm_container_app" "{terraform_name}" {{

  name                         = "{resource_name}"
  resource_group_name          = "{destination_rg}"
  container_app_environment_id = azurerm_container_app_environment.{terraform_env_name}.id

  revision_mode = "{revision_mode}"

{registry_block}
{ingress_block}
{identity_block}
{secret_block}

  template {{
    min_replicas = {app.get("min_replicas", 0)}
    max_replicas = {app.get("max_replicas", 10)}

    container {{
      name   = "{resource_name}"
      image  = "{image}"
      cpu    = {cpu}
      memory = "{memory}"

{env_block}
    }}
  }}
}}
'''

        # -------------------------------
        # Container App Environment
        # -------------------------------
        elif "Microsoft.App/managedEnvironments" in resource_type:

            tf_code = f'''
resource "azurerm_container_app_environment" "{terraform_name}" {{
  name                = "{resource_name}"
  location            = "{destination_region}"
  resource_group_name = "{destination_rg}"
}}
'''

        else:
            return {"status": "unsupported"}

        # -------------------------------
        # Write TF file
        # -------------------------------
        filename = f"terraform/generated/{terraform_name}.tf"

        try:
            with open(filename, "w") as f:
                f.write(tf_code)
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return {"status": "generated", "file": filename}