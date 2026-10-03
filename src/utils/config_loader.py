"""YAML config loading utilities. All pipeline configuration flows through here."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from src.utils.logger import get_logger

logger = get_logger(__name__)

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


def ranking_path(config: dict[str, Any]) -> Path:
    """Where the ranking for `feature_selection.ranking_source` lives (one file per source)."""
    path = resolve_path(config["paths"]["feature_ranking"].format(source=config["feature_selection"]["ranking_source"]))
    return path.with_name(tagged(config, path.name))  # the target (hence MI ranking) depends on the label scheme


def _ranked_pool(config: dict[str, Any], feature_sets: dict[str, Any]) -> list[str]:
    """Features ordered most -> least important for `feature_selection.ranking_source`:
    "curated" is the hand-written feature_curated_rank; "mutual_info" is the data-derived
    ranking file written by run_all_experiments (or train_pipeline.py --write-ranking).
    Raises if that file is missing or doesn't match the pool — never falls back silently."""
    pool = set(feature_sets["feature_pool"])
    if config["feature_selection"]["ranking_source"] == "curated":
        ranked = list(feature_sets["feature_curated_rank"])
    else:
        path = ranking_path(config)
        if not path.exists():
            raise FileNotFoundError(f"Feature ranking {path} not found. Generate it with "
                                    f"`python pipelines/run_all_experiments.py` or `python pipelines/train_pipeline.py --write-ranking`.")
        ranked = pd.read_csv(path)["feature"].tolist()
    if set(ranked) != pool or len(ranked) != len(pool):
        raise ValueError(f"Feature ranking does not match feature_pool (pool-only: {sorted(pool - set(ranked))}, "
                         f"ranking-only: {sorted(set(ranked) - pool)}). Regenerate it.")
    return ranked


def get_active_features(config: dict[str, Any], feature_sets: dict[str, Any], set_name: str | None = None) -> list[str]:
    """Return the top-N features (N from the requested or config-active feature set) of the
    configured ranking."""
    set_name = set_name or config["feature_selection"]["active_set"]
    return _ranked_pool(config, feature_sets)[:feature_sets["feature_sets"][str(set_name)]]


def get_worst_features(config: dict[str, Any], feature_sets: dict[str, Any], set_name: str) -> list[str]:
    """Baseline: the N LEAST important features of the configured ranking."""
    return _ranked_pool(config, feature_sets)[::-1][:feature_sets["feature_sets"][str(set_name)]]


def get_random_features(config: dict[str, Any], feature_sets: dict[str, Any], set_name: str, draw: int = 0) -> list[str]:
    """Baseline: N features drawn at random from the pool; `draw` selects an independent
    subset (seed = project.seed + draw)."""
    pool = sorted(feature_sets["feature_pool"])
    rng = np.random.default_rng(config["project"]["seed"] + draw)
    return list(rng.permutation(pool)[:feature_sets["feature_sets"][str(set_name)]])


def get_label_scheme(config: dict[str, Any]) -> tuple[str, dict[str, list[str]], bool]:
    """(name, merge_groups, hierarchical) of the active `data.label_scheme`, from `data.label_schemes`."""
    name = config["data"]["label_scheme"]
    schemes = config["data"]["label_schemes"]
    if name not in schemes:
        raise KeyError(f"Unknown data.label_scheme '{name}' (known: {sorted(schemes)})")
    return name, schemes[name].get("merge_groups") or {}, bool(schemes[name].get("hierarchical"))


def scheme_tag(config: dict[str, Any]) -> str:
    """Filename suffix of the active output variant: the label scheme ("" for the default
    "current", else "_<name>"), `feature_selection.variant_tag` (e.g. "_nonredundant"; unset by
    default) and the feature pool ("_48f" for the full pool, set by choose_pool; "" for the
    40-feature base pool), so a non-default run's outputs never overwrite the default's and the
    two pools' results (and rankings) coexist."""
    name = config["data"]["label_scheme"]
    fs = config["feature_selection"]
    return ("" if name == "current" else f"_{name}") + fs.get("variant_tag", "") + fs.get("pool_tag", "")


def tagged(config: dict[str, Any], filename: str) -> str:
    """`filename` with the scheme tag inserted before the extension (unchanged for "current")."""
    p = Path(filename)
    return f"{p.stem}{scheme_tag(config)}{p.suffix}"


def choose_pool(config: dict[str, Any], feature_sets: dict[str, Any], columns) -> tuple[dict, dict]:
    """Pick the feature pool for the loaded data per `feature_selection.pool`: "auto" uses
    `feature_pool_full` when every extra official column it adds is present in `columns`, else
    `feature_pool`; "base" forces the 40-feature pool (even if the columns exist, for a like-for-like
    comparison); "full" requires the columns. Returns (config, feature_sets) copies with the pool
    (and, for the full pool, the tier list `experiments.feature_sets_full`) applied,
    `feature_sets["pool_name"]` set to "full" or "base" and `feature_selection.pool_tag` ("_48f" for
    full, which scheme_tag adds to every output name); the choice is logged."""
    config, feature_sets = copy.deepcopy(config), copy.deepcopy(feature_sets)
    full = feature_sets.get("feature_pool_full")
    raw_extra = set(full or []) - set(feature_sets["feature_pool"])  # the extra official columns
    missing = sorted(raw_extra - set(columns))
    want = config["feature_selection"].get("pool", "auto")
    if want not in ("auto", "base", "full"):
        raise ValueError(f"feature_selection.pool must be auto, base or full, got {want!r}")
    if want == "full" and (full is None or missing):
        raise ValueError(f"feature_selection.pool is 'full' but the data lacks official columns: {missing}")
    use_full = want == "full" or (want == "auto" and full is not None and not missing)
    feature_sets["pool_name"] = "full" if use_full else "base"
    config["feature_selection"]["pool_tag"] = "_48f" if use_full else ""
    if use_full:
        feature_sets["feature_pool"] = list(full)
        config["experiments"]["feature_sets"] = list(config["experiments"]["feature_sets_full"])
    logger.info(f"Feature pool: '{feature_sets['pool_name']}' ({len(feature_sets['feature_pool'])} features)"
                + (f"; missing official columns: {missing}" if missing and not use_full else ""))
    return config, feature_sets


def resolve_path(relative_path: str | Path) -> Path:
    """Resolve a path relative to the project root so pipelines work from any cwd."""
    p = Path(relative_path)
    return p if p.is_absolute() else PROJECT_ROOT / p


# XGBoost's native model format is JSON; every other model type is a joblib pickle.
_ARTIFACT_SUFFIX = {"xgboost": ".json"}


def artifact_suffix(model_type: str) -> str:
    """File extension of a saved model artifact for this model.type (".json" or ".pkl")."""
    return _ARTIFACT_SUFFIX.get(model_type, ".pkl")


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
    tag = scheme_tag(config)
    model_path = model_dir / f"{model_type}_{feature_set}_closed{tag}{artifact_suffix(model_type)}"
    preprocessor_path = model_dir / f"preprocessor_{feature_set}{tag}.pkl"
    return model_path, preprocessor_path


def get_metrics_dir(config: dict[str, Any]) -> Path:
    """Directory for a model type's CSV outputs: results/metrics/<model.type>/ —
    mirrors get_dashboard_paths' reasoning and results/plots/<model.type>/: every
    experiment/evaluation/diagnostic CSV is namespaced by model.type, so training a
    different model never silently overwrites another model's reported numbers.
    Created on demand by the caller (mkdir(parents=True, exist_ok=True)).
    """
    return resolve_path(config["paths"]["results_dir"]) / "metrics" / config["model"]["type"]
