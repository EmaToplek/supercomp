"""Endpoint for the frontend to check whether an API key is valid."""

from fastapi import APIRouter, Depends

from app.auth import require_api_key

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/check", dependencies=[Depends(require_api_key)])
def check_api_key():
    """Returns 200 for a valid key; require_api_key returns 401 otherwise."""
    return {"valid": True}