"""Structured logging setup shared by every module. Import get_logger(__name__) instead of print()."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

_CONFIGURED = False
_FILE_HANDLER_PATHS: set[str] = set()
_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def _configure_root(level: str = "INFO") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO),
                         format=_FORMAT, handlers=[logging.StreamHandler(sys.stdout)], force=True)
    _CONFIGURED = True


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Return a configured module-level logger. Safe to call repeatedly."""
    _configure_root(level=level)
    return logging.getLogger(name)


def add_file_logging(log_file: str) -> None:
    """Attach a file handler to the root logger so a pipeline run can be tailed from
    disk (e.g. `Get-Content -Wait results/pipeline.log`) instead of only console output.

    Call once from a script's entrypoint after loading config — safe to call multiple
    times or from multiple entrypoints; the same path is only attached once.
    """
    log_path = Path(log_file)
    key = str(log_path.resolve())
    if key in _FILE_HANDLER_PATHS:
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter(_FORMAT))
    logging.getLogger().addHandler(handler)
    _FILE_HANDLER_PATHS.add(key)
