from fastapi import FastAPI
from dbr.api.work_items import router as work_items_router
from dbr.api.schedules import router as schedules_router
from dbr.api.system import router as system_router
from dbr.api.auth import router as auth_router
from scalar_fastapi import get_scalar_api_reference

app = FastAPI(
    title="DBR Buffer Management System API",
    version="1.0.0",
    description="API for managing Collections, Work Items, and Schedules within a Drum Buffer Rope (DBR) system",
    servers=[
        {"url": "http://127.0.0.1:8000", "description": "Local server"},
    ],
)

# Include API routers
app.include_router(work_items_router, prefix="/api/v1")
app.include_router(schedules_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "DBR Buffer Management System API", "version": "1.0.0"}


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )
