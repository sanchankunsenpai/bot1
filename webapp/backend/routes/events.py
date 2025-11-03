"""Event and attendance endpoints."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ...shared import attendance as attendance_service
from ...shared import events as event_service, logs
from ..models import schemas
from ..utils.deps import get_current_user

router = APIRouter(prefix="/events", tags=["events"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[schemas.EventResponse])
def list_events(alliance_id: int | None = None):
    return event_service.list_events(alliance_id)


@router.post("/", response_model=schemas.EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(payload: schemas.EventCreate):
    event_id = event_service.create_event(
        payload.name,
        payload.start_time.isoformat(),
        description=payload.description,
        end_time=payload.end_time.isoformat() if payload.end_time else None,
        reminder_minutes=payload.reminder_minutes,
        alliance_id=payload.alliance_id,
    )
    logs.record_log("events", f"Event created: {payload.name}")
    event = event_service.get_event(event_id)
    assert event is not None
    return event


@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(event_id: int, payload: schemas.EventUpdate):
    try:
        event_service.update_event(
            event_id,
            name=payload.name,
            description=payload.description,
            start_time=payload.start_time.isoformat() if payload.start_time else None,
            end_time=payload.end_time.isoformat() if payload.end_time else None,
            reminder_minutes=payload.reminder_minutes,
            alliance_id=payload.alliance_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    logs.record_log("events", f"Event updated: {event_id}")
    event = event_service.get_event(event_id)
    assert event is not None
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int):
    event_service.delete_event(event_id)
    logs.record_log("events", f"Event deleted: {event_id}")
    return {"message": "deleted"}


@router.get("/{event_id}/attendance", response_model=List[dict])
def get_attendance(event_id: int):
    return attendance_service.list_attendance(event_id)


@router.post("/{event_id}/attendance", status_code=status.HTTP_200_OK)
def update_attendance(event_id: int, updates: List[schemas.AttendanceUpdate]):
    for entry in updates:
        attendance_service.upsert_attendance(event_id, entry.member_id, entry.status)
    logs.record_log("attendance", f"Attendance updated for event {event_id}")
    return {"message": "updated"}


@router.get("/summary/{alliance_id}", response_model=List[schemas.AttendanceSummaryResponse])
def get_summary(alliance_id: int):
    return attendance_service.attendance_summary(alliance_id)


__all__ = ["router"]
