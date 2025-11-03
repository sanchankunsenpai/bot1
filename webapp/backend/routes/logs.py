"""Audit log endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from ...shared import logs as log_service
from ..models import schemas
from ..utils.deps import get_current_user

router = APIRouter(prefix="/logs", tags=["logs"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[schemas.LogEntry])
def list_logs(limit: int = 200):
    return log_service.list_logs(limit)


__all__ = ["router"]
