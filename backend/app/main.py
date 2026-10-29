from contextlib import asynccontextmanager
from fastapi import FastAPI

from app import models
from app.database import init_db
from app.routes import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Supercomp API", lifespan=lifespan)
app.include_router(settings.router)

@app.get("/")
def root():
    return {"message": "API is running"}