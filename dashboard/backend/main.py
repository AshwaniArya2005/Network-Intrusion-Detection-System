"""FastAPI app entrypoint. Run from the project root:

    uvicorn dashboard.backend.main:app --reload --port 8000
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dashboard.backend.api import router
from src.utils.config_loader import load_config, resolve_path
from src.utils.logger import add_file_logging

add_file_logging(str(resolve_path(load_config()["logging"]["log_file"])))

app = FastAPI(title="XAI Network IDS API", version="1.0.0")

# Dev-friendly CORS: any localhost port, so the Vite dashboard can run on whichever
# port is free. Tighten before deploying this anywhere beyond localhost.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
