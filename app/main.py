from fastapi import FastAPI
from app.routers import router

app = FastAPI(title="name")
app.include_router(router)