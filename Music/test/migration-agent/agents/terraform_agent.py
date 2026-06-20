import os
import json


class TerraformAgent:

    def generate(
        self,
        resource,
        destination_region,
        destination_rg
    ):

        os.makedirs(
            "terraform/generated",
            exist_ok=True
        )

        resource_type = getattr(resource, "resource_type", "")
        resource_name = getattr(resource, "name", None)

        if not resource_name:
            return {
                "status": "error",
                "message": "Resource name is missing"
            }

        # -------------------------------
        # Container Registry (ACR)
        # -------------------------------
        if "Microsoft.ContainerRegistry" in resource_type:

            acr_export_file = f"exports/acr/{resource_name}.json"

            if not os.path.exists(acr_export_file):
                return {
                    "status": "error",
                    "message": f"Export file not found: {acr_export_file}"
                }

            try:
                with open(acr_export_file) as f:
                    acr_details = json.load(f)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to read {acr_export_file}: {str(e)}"
                }

            config = acr_details.get("configuration", {})
            sku = config.get("sku", "Basic")
            admin_enabled = config.get("admin_user_enabled", False)

            tf_code = f'''
resource "azurerm_container_registry" "{resource_name}" {{
  name                = "{resource_name}"
  location            = "{destination_region}"
  resource_group_name = "{destination_rg}"

  sku           = "{sku}"
  admin_enabled = {str(admin_enabled).lower()}
}}
'''

        # -------------------------------
        # App Service Plan (serverFarms)
        # -------------------------------
        elif "Microsoft.Web/serverFarms" in resource_type:

            terraform_plan_name = resource_name.replace("-", "_")

            tf_code = f'''
resource "azurerm_service_plan" "{terraform_plan_name}" {{
  name                = "{resource_name}"
  location            = "{destination_region}"
  resource_group_name = "{destination_rg}"

  os_type  = "Linux"
  sku_name = "B1"
}}
'''

        # -------------------------------
        # Web App (Microsoft.Web/sites)
        # -------------------------------
        elif "Microsoft.Web/sites" in resource_type:

            app_export_file = f"exports/appservice/{resource_name}.json"

            if not os.path.exists(app_export_file):
                return {
                    "status": "error",
                    "message": f"Export file not found: {app_export_file}"
                }

            try:
                with open(app_export_file) as f:
                    app_details = json.load(f)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to read {app_export_file}: {str(e)}"
                }

            server_farm_name = app_details.get("server_farm_name")

            if not server_farm_name:
                return {
                    "status": "error",
                    "message": f"server_farm_name missing in {app_export_file}"
                }

            terraform_plan_name = server_farm_name.replace("-", "_")

            linux_fx_version = app_details.get("linux_fx_version", "")
            always_on = app_details.get("always_on", False)
            ftps_state = app_details.get("ftps_state", "Disabled")

            python_version = None
            if "PYTHON|" in linux_fx_version:
                python_version = linux_fx_version.split("|")[1]

            app_settings = app_details.get("app_settings", {})
            identity = app_details.get("identity")
            connection_strings = app_details.get("connection_strings", {})
            deployment_slots = app_details.get("deployment_slots", [])
            vnet_integration = app_details.get("vnet_integration")
            custom_domains = app_details.get("custom_domains", [])
            certificates = app_details.get("certificates", [])
            private_endpoints = app_details.get("private_endpoints", [])

            tf_code = f'''
resource "azurerm_linux_web_app" "{resource_name}" {{
  name                = "{resource_name}"
  location            = "{destination_region}"
  resource_group_name = "{destination_rg}"

  service_plan_id = azurerm_service_plan.{terraform_plan_name}.id

  site_config {{
    always_on  = {str(always_on).lower()}
    ftps_state = "{ftps_state}"
  }}

  application_stack {{
    python_version = "{python_version or "3.8"}"
  }}
'''

            if app_settings:
                tf_code += "\n  app_settings = {\n"
                for k, v in app_settings.items():
                    tf_code += f'    {k} = "{v}"\n'
                tf_code += "  }\n"

            if identity:
                tf_code += f'''
  identity {{
    type = "{identity.get("type")}"
  }}
'''

            if vnet_integration:
                tf_code += f'''
  virtual_network_subnet_id = "{vnet_integration}"
'''

            tf_code += "\n}\n"

            for name, cfg in connection_strings.items():
                tf_code += f'''
resource "azurerm_app_service_connection_string" "{resource_name}_{name}" {{
  name  = "{name}"
  type  = "{cfg.get("type")}"
  value = "{cfg.get("value")}"

  app_service_id = azurerm_linux_web_app.{resource_name}.id
}}
'''

            for slot in deployment_slots:
                slot_name = slot.get("name")
                if not slot_name:
                    continue

                slot_tf_name = slot_name.replace("-", "_")

                tf_code += f'''
resource "azurerm_linux_web_app_slot" "{slot_tf_name}" {{

  name           = "{slot_name}"

  app_service_id = azurerm_linux_web_app.{resource_name}.id
}}
'''

            for domain in custom_domains:
                label = domain.replace(".", "_")

                tf_code += f'''
resource "azurerm_app_service_custom_hostname_binding" "{label}" {{

  hostname = "{domain}"

  app_service_name = azurerm_linux_web_app.{resource_name}.name
}}
'''

            for cert in certificates:
                cert_name = cert.get("name")
                if not cert_name:
                    continue

                cert_tf_name = cert_name.replace("-", "_")

                tf_code += f'''
resource "azurerm_app_service_certificate" "{cert_tf_name}" {{

  name                = "{cert_name}"
  resource_group_name = "{destination_rg}"

  pfx_blob = "{cert.get("pfx_blob", "")}"
  password = "{cert.get("password", "")}"
}}
'''

            for pe in private_endpoints:
                pe_name = pe.get("name")
                subnet_id = pe.get("subnet_id")

                if not pe_name or not subnet_id:
                    continue

                pe_tf_name = pe_name.replace("-", "_")

                tf_code += f'''
resource "azurerm_private_endpoint" "{pe_tf_name}" {{

  name                = "{pe_name}"
  location            = "{destination_region}"
  resource_group_name = "{destination_rg}"
  subnet_id           = "{subnet_id}"

  private_service_connection {{
    name                           = "{pe.get("connection_name", f"{resource_name}-pe")}"
    private_connection_resource_id = azurerm_linux_web_app.{resource_name}.id
    is_manual_connection          = false
    subresource_names             = ["sites"]
  }}
}}
'''

        # -------------------------------
        # Container Apps (Microsoft.App/containerApps)
        # -------------------------------
        elif "Microsoft.App/containerApps" in resource_type:

            export_file = f"exports/containerapp/{resource_name}.json"

            if not os.path.exists(export_file):
                return {
                    "status": "error",
                    "message": f"Export file not found: {export_file}"
                }

            try:
                with open(export_file) as f:
                    app = json.load(f)
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to read {export_file}: {str(e)}"
                }

            image = app.get("image")
            if not image:
                return {
                    "status": "error",
                    "message": f"Missing image in {export_file}"
                }

            environment_id = app.get("environment_id")
            if not environment_id:
                return {
                    "status": "error",
                    "message": f"Missing environment_id in {export_file}"
                }

            cpu = app.get("cpu", 0.5)
            memory = app.get("memory", "1Gi")
            revision_mode = app.get("revision_mode", "Single")
            min_replicas = app.get("min_replicas", 0)
            max_replicas = app.get("max_replicas", 10)

            env_name = environment_id.split("/")[-1]
            terraform_env_name = env_name.replace("-", "_")

            tf_code = f'''
resource "azurerm_container_app" "{resource_name}" {{

  name                         = "{resource_name}"
  resource_group_name          = "{destination_rg}"
  container_app_environment_id = azurerm_container_app_environment.{terraform_env_name}.id

  revision_mode = "{revision_mode}"

  template {{

    min_replicas = {min_replicas}
    max_replicas = {max_replicas}

    container {{
      name   = "{resource_name}"
      image  = "{image}"
      cpu    = {cpu}
      memory = "{memory}"
    }}
  }}
}}
'''

        # -------------------------------
        # Container App Environment
        # -------------------------------
        elif "Microsoft.App/managedEnvironments" in resource_type:

            tf_code = f'''
resource "azurerm_container_app_environment" "{resource_name}" {{

  name                = "{resource_name}"
  location            = "{destination_region}"
  resource_group_name = "{destination_rg}"

}}
'''

        # -------------------------------
        # Unsupported
        # -------------------------------
        else:
            return {
                "status": "unsupported"
            }

        # -------------------------------
        # Write TF file
        # -------------------------------
        filename = f"terraform/generated/{resource_name}.tf"

        try:
            with open(filename, "w") as f:
                f.write(tf_code)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to write TF file: {str(e)}"
            }

        return {
            "status": "generated",
            "file": filename
        }