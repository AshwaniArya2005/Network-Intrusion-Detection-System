"""YAML config loading utilities. All pipeline configuration flows through here."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file into a dict. Paths may be relative to the project root."""
    p = Path(path)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config(config_path: str | Path = "configs/config.yaml") -> dict[str, Any]:
    """Load the main pipeline config."""
    return load_yaml(config_path)


def load_feature_sets(config_path: str | Path = "configs/feature_sets.yaml") -> dict[str, Any]:
    """Load the feature set definitions."""
    return load_yaml(config_path)


def get_active_features(config: dict[str, Any], feature_sets: dict[str, Any], set_name: str | None = None) -> list[str]:
    """Return the ordered feature-name list for the requested (or config-active) feature set size."""
    set_name = set_name or config["feature_selection"]["active_set"]
    n = feature_sets["feature_sets"][str(set_name)]
    ranked = feature_sets["feature_importance_rank"]
    return ranked[:n]


def resolve_path(relative_path: str | Path) -> Path:
    """Resolve a path relative to the project root so pipelines work from any cwd."""
    p = Path(relative_path)
    return p if p.is_absolute() else PROJECT_ROOT / p


def get_dashboard_paths(config: dict[str, Any]) -> tuple[Path, Path]:
    """Derive the dashboard's model + preprocessor paths from `model.type` and
    `dashboard.feature_set` — the single source of truth is `model.type`, not a
    separately hardcoded path. Switching `model.type` in config.yaml and retraining
    is then enough on its own; there's no second path to remember to update, and no
    risk of the dashboard silently loading a stale model saved by a different model type.
    """
    model_type = config["model"]["type"]
    feature_set = config["dashboard"]["feature_set"]
    model_dir = resolve_path(config["paths"]["models_dir"]) / model_type
    model_path = model_dir / f"{model_type}_{feature_set}_closed.pkl"
    preprocessor_path = model_dir / f"preprocessor_{feature_set}.pkl"
    return model_path, preprocessor_path
