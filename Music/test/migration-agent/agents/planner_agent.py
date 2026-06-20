class PlannerAgent:

    def create_plan(self, resource, destination_region, destination_rg):

        resource_type = resource.resource_type

        if "Microsoft.Web/serverFarms" in resource_type:

            actions = [
                "Create App Service Plan",
                "Configure SKU",
                "Validate Plan"
            ]

        elif "Microsoft.Web/sites" in resource_type:

            actions = [
                "Create App Service",
                "Apply App Settings",
                "Deploy Application",
                "Validate Endpoint"
            ]

        elif "Microsoft.ContainerRegistry" in resource_type:

            actions = [
                "Create ACR",
                "Enable Admin User",
                "Import Images",
                "Validate Repositories"
            ]

        elif "Microsoft.OperationalInsights/workspaces" in resource_type:

            actions = [
                "Create Log Analytics Workspace",
                "Configure Retention",
                "Link Monitoring Resources",
                "Validate Workspace"
            ]

        else:

            actions = [
                "Export Configuration",
                "Generate Terraform",
                "Deploy Resource",
                "Validate Deployment"
            ]

        return {
            "resource_name": resource.name,
            "resource_type": resource_type,
            "source_region": resource.location,
            "target_region": destination_region,
            "target_resource_group": destination_rg,
            "actions": actions
        }