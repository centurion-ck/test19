from fastapi import FastAPI

from api.discovery import router as discovery_router

app = FastAPI(
    title="Azure Migration Agent",
    version="1.0"
)

app.include_router(
    discovery_router,
    prefix="/api"
)


@app.get("/")
def health():

    return {
        "status": "running"
    }