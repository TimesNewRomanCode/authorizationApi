from fastapi import FastAPI

from app.core.redis import redis_service
from app.routers import router

app = FastAPI(title="Auth")

@app.on_event("startup")
async def startup_event():
    await redis_service.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await redis_service.disconnect()

app.include_router(router)