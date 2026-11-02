"""Shared route dependencies."""

import os

from fastapi import HTTPException, status


def block_in_demo_mode():
    """Reject write requests on the public demo, so nobody can upload their health data there."""
    if os.getenv("DEMO_MODE", "false").lower() == "true":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not available in the public demo",
        )
