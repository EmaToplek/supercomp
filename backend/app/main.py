from contextlib import asynccontextmanager
from fastapi import FastAPI
from app import init_db, SessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Supercomp API", lifespan=lifespan)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "API is running and database is connected!"}