"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ...shared import auth as auth_utils
from ..models import schemas
from ..utils.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.LoginResponse)
def login(payload: schemas.LoginRequest, request: Request):
    user = auth_utils.authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role
    return schemas.LoginResponse(username=user.username, role=user.role)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}


@router.get("/me", response_model=schemas.LoginResponse)
def get_me(user=Depends(get_current_user)):
    return schemas.LoginResponse(username=user.username, role=user.role)


__all__ = ["router"]
