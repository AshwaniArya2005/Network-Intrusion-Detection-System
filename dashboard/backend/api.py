"""API endpoints: /predict (upload a flow CSV, get predictions + explanations), /health."""
from __future__ import annotations

import io

import pandas as pd
from fastapi import APIRouter, HTTPException, UploadFile

from dashboard.backend.prediction_service import get_prediction_service
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10MB


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/predict")
async def predict(file: UploadFile) -> dict:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")

    raw = await file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 10MB).")

    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded CSV has no rows.")

    try:
        service = get_prediction_service()
        predictions = service.predict(df)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    return {"n_rows": len(df), "predictions": predictions}
