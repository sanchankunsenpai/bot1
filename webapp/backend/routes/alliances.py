"""Alliance REST endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ...shared import alliances as alliance_service, logs
from ..models import schemas
from ..utils.deps import get_current_user

router = APIRouter(prefix="/alliances", tags=["alliances"], dependencies=[Depends(get_current_user)])


def _serialize_alliance(raw: dict) -> schemas.AllianceResponse:
    return schemas.AllianceResponse(
        id=int(raw["id"]),
        name=raw["name"],
        discord_server_id=raw.get("discord_server_id"),
        interval_minutes=int(raw.get("interval_minutes", 0) or 0),
        channel_id=raw.get("channel_id"),
        member_count=int(raw.get("member_count", 0) or 0),
    )


@router.get("/", response_model=List[schemas.AllianceResponse])
def get_alliances():
    return [_serialize_alliance(alliance) for alliance in alliance_service.list_alliances()]


@router.post("/", response_model=schemas.AllianceResponse, status_code=status.HTTP_201_CREATED)
def create_alliance(payload: schemas.AllianceCreate):
    alliance_id = alliance_service.create_alliance(
        payload.name,
        payload.discord_server_id,
        payload.interval_minutes,
        channel_id=payload.channel_id,
    )
    logs.record_log("alliances", f"Alliance created: {payload.name}")
    alliance = alliance_service.get_alliance(alliance_id)
    assert alliance is not None
    return _serialize_alliance(alliance)


@router.get("/{alliance_id}", response_model=schemas.AllianceResponse)
def get_alliance(alliance_id: int):
    alliance = alliance_service.get_alliance(alliance_id)
    if not alliance:
        raise HTTPException(status_code=404, detail="Alliance not found")
    return _serialize_alliance(alliance)


@router.put("/{alliance_id}", response_model=schemas.AllianceResponse)
def update_alliance(alliance_id: int, payload: schemas.AllianceUpdate):
    try:
        alliance_service.update_alliance(
            alliance_id,
            name=payload.name,
            discord_server_id=payload.discord_server_id,
            interval_minutes=payload.interval_minutes,
            channel_id=payload.channel_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    logs.record_log("alliances", f"Alliance updated: {alliance_id}")
    alliance = alliance_service.get_alliance(alliance_id)
    assert alliance is not None
    return _serialize_alliance(alliance)


@router.delete("/{alliance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alliance(alliance_id: int):
    alliance_service.delete_alliance(alliance_id)
    logs.record_log("alliances", f"Alliance deleted: {alliance_id}")
    return {"message": "deleted"}


__all__ = ["router"]
