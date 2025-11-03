"""Alliance member endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ...shared import alliances as alliance_service, logs
from ..models import schemas
from ..utils.deps import get_current_user

router = APIRouter(prefix="/members", tags=["members"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[schemas.MemberResponse])
def get_members(alliance_id: int | None = None):
    return alliance_service.list_members(alliance_id)


@router.post("/", response_model=schemas.MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(payload: schemas.MemberCreate):
    member_id = alliance_service.add_member(
        payload.alliance_id,
        payload.name,
        fl_level=payload.fl_level,
        title=payload.title,
        joined_at=payload.joined_at,
        notes=payload.notes,
    )
    logs.record_log("members", f"Member added: {payload.name}")
    members = alliance_service.list_members(payload.alliance_id)
    member = next((m for m in members if m["id"] == member_id), None)
    assert member is not None
    return member


@router.put("/{member_id}", response_model=schemas.MemberResponse)
def update_member(member_id: int, payload: schemas.MemberUpdate):
    try:
        alliance_service.update_member(
            member_id,
            name=payload.name,
            fl_level=payload.fl_level,
            title=payload.title,
            joined_at=payload.joined_at,
            notes=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    logs.record_log("members", f"Member updated: {member_id}")
    members = alliance_service.list_members()
    member = next((m for m in members if m["id"] == member_id), None)
    assert member is not None
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int):
    alliance_service.remove_member(member_id)
    logs.record_log("members", f"Member removed: {member_id}")
    return {"message": "deleted"}


__all__ = ["router"]
