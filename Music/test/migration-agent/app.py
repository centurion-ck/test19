from fastapi import FastAPI

from api.discovery import router as discovery_router
from api.migration import router as migration_router
from api.terraform import router as terraform_router
from api.migration_request import router as migration_request_router
from api.export import router as export_router
from api.resource_details import router as resource_details_router

from api.dependency import (
    router as dependency_router
)

from api.export_package import (
    router as export_package_router
)



app = FastAPI(
    title="Azure Migration Agent",
    version="1.0"
)

app.include_router(
    discovery_router,
    prefix="/api"
)

app.include_router(
    migration_router,
    prefix="/api"
)

app.include_router(
    terraform_router,
    prefix="/api"
)

app.include_router(
    migration_request_router,
    prefix="/api"
)

app.include_router(
    resource_details_router,
    prefix="/api"
)

app.include_router(
    export_router,
    prefix="/api"
)

app.include_router(
    dependency_router,
    prefix="/api"
)

@app.get("/")
def health():

    return {
        "status": "running"
    }

app.include_router(
    export_package_router,
    prefix="/api"
)