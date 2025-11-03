"""Alliance member endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ...shared import alliances as alliance_service, logs
from ..models import schemas
from ..utils.deps import get_current_user

router = APIRouter(prefix="/members", tags=["members"], dependencies=[Depends(get_current_user)])


def _serialize_member(raw: dict) -> schemas.MemberResponse:
    return schemas.MemberResponse(
        id=int(raw["fid"]),
        alliance_id=raw.get("alliance_id"),
        name=raw.get("nickname"),
        fl_level=raw.get("furnace_lv"),
        title=None,
        joined_at=None,
        notes=raw.get("stove_lv_content"),
        alliance_name=raw.get("alliance_name"),
    )


@router.get("/", response_model=List[schemas.MemberResponse])
def get_members(alliance_id: int | None = None):
    return [_serialize_member(member) for member in alliance_service.list_members(alliance_id)]


@router.post("/", response_model=schemas.MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(payload: schemas.MemberCreate):
    member_id = alliance_service.add_member(
        None,
        payload.name,
        alliance_id=payload.alliance_id,
        furnace_lv=payload.fl_level,
        stove_lv_content=payload.notes,
    )
    logs.record_log("members", f"Member added: {payload.name}")
    member = alliance_service.get_member(member_id)
    assert member is not None
    return _serialize_member(member)


@router.put("/{member_id}", response_model=schemas.MemberResponse)
def update_member(member_id: int, payload: schemas.MemberUpdate):
    try:
        alliance_service.update_member(
            member_id,
            nickname=payload.name,
            furnace_lv=payload.fl_level,
            stove_lv_content=payload.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    logs.record_log("members", f"Member updated: {member_id}")
    member = alliance_service.get_member(member_id)
    assert member is not None
    return _serialize_member(member)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int):
    alliance_service.remove_member(member_id)
    logs.record_log("members", f"Member removed: {member_id}")
    return {"message": "deleted"}


__all__ = ["router"]
