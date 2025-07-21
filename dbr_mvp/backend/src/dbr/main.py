from fastapi import FastAPI
from dbr.api.work_items import router as work_items_router
from dbr.api.schedules import router as schedules_router
from dbr.api.system import router as system_router

app = FastAPI(
    title="DBR Buffer Management System API",
    version="1.0.0",
    description="API for managing Collections, Work Items, and Schedules within a Drum Buffer Rope (DBR) system"
)

# Include API routers
app.include_router(work_items_router, prefix="/api/v1")
app.include_router(schedules_router, prefix="/api/v1")
app.include_router(system_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "DBR Buffer Management System API", "version": "1.0.0"}