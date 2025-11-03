"""Gift code endpoints including OCR support."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from ...shared import gift_codes as gift_service, logs
from ...shared.gift_captcha_solver import GiftCaptchaSolver, ONNX_AVAILABLE
from ..models import schemas
from ..utils.deps import get_current_user

router = APIRouter(prefix="/gift-codes", tags=["gift-codes"], dependencies=[Depends(get_current_user)])
_solver = GiftCaptchaSolver()


@router.get("/", response_model=List[dict])
def list_gift_codes(alliance_id: int | None = None):
    return gift_service.list_gift_codes(alliance_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_gift_code(payload: schemas.GiftCodeCreate):
    gift_id = gift_service.upsert_gift_code(payload.code, alliance_id=payload.alliance_id)
    logs.record_log("gift", f"Gift code tracked: {payload.code}")
    return gift_service.list_gift_codes(payload.alliance_id if payload.alliance_id else None)


@router.post("/solve")
async def solve_captcha(file: UploadFile = File(...)):
    if not ONNX_AVAILABLE:
        raise HTTPException(status_code=500, detail="ONNX runtime not available")

    image_bytes = await file.read()
    result = await _solver.solve_captcha(image_bytes)
    logs.record_log("gift", f"Captcha solved (success={result.success})")
    return {
        "code": result.code,
        "success": result.success,
        "confidence": result.confidence,
        "duration": result.duration,
    }


@router.put("/{gift_id}")
def update_gift_code(gift_id: int, payload: schemas.GiftCodeUpdate):
    gift_service.update_gift_code_status(gift_id, payload.status, redeemed_by=payload.redeemed_by)
    logs.record_log("gift", f"Gift code updated: {gift_id}")
    return {"message": "updated"}


@router.delete("/{gift_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gift_code(gift_id: int):
    gift_service.delete_gift_code(gift_id)
    logs.record_log("gift", f"Gift code deleted: {gift_id}")
    return {"message": "deleted"}


__all__ = ["router"]
