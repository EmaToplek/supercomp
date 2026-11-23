import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_db
from app.garmin_client import GarminClient, GarminError
from app.garmin_sync import sync_garmin
from app.schemas import SyncOut

router = APIRouter(prefix="/sync", tags=["sync"])


def get_garmin_client():
    key = os.getenv("GARMIN_PERSONAL_KEY")
    if not key:
        raise HTTPException(status_code=503, detail="Garmin sync is not configured on the server")
    client = GarminClient(key)
    try:
        yield client
    finally:
        client.close()


@router.post("", response_model=SyncOut, dependencies=[Depends(require_api_key)])
def sync(db: Session = Depends(get_db), client: GarminClient = Depends(get_garmin_client)):
    try:
        client.login()
        return sync_garmin(db, client)
    except GarminError as e:
        raise HTTPException(status_code=502, detail=f"Garmin: {e}")