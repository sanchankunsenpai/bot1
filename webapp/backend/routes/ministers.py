"""Minister scheduling endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ...shared import logs, ministers as minister_service
from ..models import schemas
from ..utils.deps import get_current_user

router = APIRouter(prefix="/ministers", tags=["ministers"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[schemas.MinisterResponse])
def list_ministers(alliance_id: int | None = None):
    return minister_service.list_ministers(alliance_id)


@router.post("/", response_model=schemas.MinisterResponse, status_code=status.HTTP_201_CREATED)
def create_minister(payload: schemas.MinisterCreate):
    minister_id = minister_service.create_minister(
        payload.alliance_id,
        payload.role,
        payload.player_name,
        payload.start_time.isoformat(),
        payload.end_time.isoformat(),
        notes=payload.notes,
    )
    logs.record_log("ministers", f"Minister slot booked: {payload.player_name}")
    ministers = minister_service.list_ministers(payload.alliance_id)
    minister = next((m for m in ministers if m["id"] == minister_id), None)
    assert minister is not None
    return minister


@router.put("/{minister_id}", response_model=schemas.MinisterResponse)
def update_minister(minister_id: int, payload: schemas.MinisterUpdate):
    try:
        minister_service.update_minister(
            minister_id,
            alliance_id=payload.alliance_id,
            role=payload.role,
            player_name=payload.player_name,
            start_time=payload.start_time.isoformat() if payload.start_time else None,
            end_time=payload.end_time.isoformat() if payload.end_time else None,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    logs.record_log("ministers", f"Minister updated: {minister_id}")
    ministers = minister_service.list_ministers()
    minister = next((m for m in ministers if m["id"] == minister_id), None)
    assert minister is not None
    return minister


@router.delete("/{minister_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_minister(minister_id: int):
    minister_service.delete_minister(minister_id)
    logs.record_log("ministers", f"Minister removed: {minister_id}")
    return {"message": "deleted"}


__all__ = ["router"]
