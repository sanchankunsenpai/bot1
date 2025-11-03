"""Pydantic schemas exposed by the API."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Authentication -----------------------------------------------------------


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    role: str


# Alliance schemas ---------------------------------------------------------


class AllianceBase(BaseModel):
    name: str
    discord_server_id: Optional[int] = None
    interval_minutes: int = Field(default=0, ge=0)


class AllianceCreate(AllianceBase):
    pass


class AllianceUpdate(BaseModel):
    name: Optional[str] = None
    discord_server_id: Optional[int] = None
    interval_minutes: Optional[int] = Field(default=None, ge=0)


class AllianceResponse(AllianceBase):
    id: int
    created_at: datetime


class MemberBase(BaseModel):
    alliance_id: int
    name: str
    fl_level: Optional[int] = None
    title: Optional[str] = None
    joined_at: Optional[str] = None
    notes: Optional[str] = None


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    fl_level: Optional[int] = None
    title: Optional[str] = None
    joined_at: Optional[str] = None
    notes: Optional[str] = None


class MemberResponse(MemberBase):
    id: int
    alliance_name: Optional[str] = None


# Gift codes ---------------------------------------------------------------


class GiftCodeCreate(BaseModel):
    code: str
    alliance_id: Optional[int] = None


class GiftCodeUpdate(BaseModel):
    status: str
    redeemed_by: Optional[str] = None


# Events and attendance ----------------------------------------------------


class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    reminder_minutes: int = Field(default=0, ge=0)
    alliance_id: Optional[int] = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    reminder_minutes: Optional[int] = Field(default=None, ge=0)
    alliance_id: Optional[int] = None


class EventResponse(EventBase):
    id: int


class AttendanceUpdate(BaseModel):
    member_id: int
    status: str


class AttendanceSummaryResponse(BaseModel):
    event_name: str
    present: int
    absent: int
    late: int


# Ministers ----------------------------------------------------------------


class MinisterBase(BaseModel):
    alliance_id: Optional[int] = None
    role: str
    player_name: str
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None


class MinisterCreate(MinisterBase):
    pass


class MinisterUpdate(BaseModel):
    alliance_id: Optional[int] = None
    role: Optional[str] = None
    player_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None


class MinisterResponse(MinisterBase):
    id: int


class LogEntry(BaseModel):
    id: int
    category: str
    message: str
    created_at: datetime


__all__ = [name for name in globals() if name.endswith("Request") or name.endswith("Response") or name.endswith("Create") or name.endswith("Update")]
