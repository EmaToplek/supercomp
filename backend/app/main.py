from contextlib import asynccontextmanager
from fastapi import FastAPI

import os
from app import models
from app.database import init_db
from app.routes import settings, activities, load, owner
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Supercomp API", lifespan=lifespan)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(owner.router)
app.include_router(settings.router)
app.include_router(activities.router)
app.include_router(load.router)


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
