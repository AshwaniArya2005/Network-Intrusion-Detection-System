"""The shared workflow for ONE model in ONE command: set model.type and model.params in configs/config.yaml (or a copy), then run

    python pipelines/run_model.py [--steps A B C] [--config path] [--pool 48] [--run-name NAME] [--out-dir DIR] [--overwrite] [--allow-synthetic]

Steps (each reuses the existing pipeline; nothing is duplicated here):
  A  headline: five seeds, official split, and the pooled random split (labelled the optimistic best case)  -> pipelines/run_headline_seeds.py
  B  feature-tier study with SHAP, plots and saved models, then its summary tables                          -> pipelines/run_tier_study.py, scripts/tier_summary.py
  C  explanation stability across the tiers                                                                 -> scripts/explanation_stability_tiers.py
A filled results table (the columns of results/TEMPLATE_model_results.csv) is written at the end by scripts/fill_model_template.py.
Cross-model SHAP agreement (needs two models: scripts/cross_model_agreement.py) and the open-set and explanation studies (XGBoost-only) stay separate commands.

Outputs go to results/metrics/<folder>/, results/plots/<folder>/ and models_saved/<folder>/, where <folder> is model.type, or model.type__NAME with --run-name
(project.run_name), so a teammate can try several hyperparameter sets side by side. Nothing of another model is touched; if the folders already hold results the
run stops unless --overwrite is given. --out-dir DIR writes results/ and models_saved/ under DIR instead (the shared feature rankings are copied there first).
"""
from __future__ import annotations

import argparse
import copy
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import yaml

from src.models.model_factory import create_model
from src.utils.config_loader import (
    CONFIG_ENV, PROJECT_ROOT, get_metrics_dir, get_models_dir, get_plots_dir, load_config, load_feature_sets, model_folder, resolve_path,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

POOLS = {"48": ("full", "48f"), "40": ("base", "40f"), "45": ("full_no_ttl", "45f")}   # --pool -> (pool name for the pipelines, file label)
STEPS = ("A", "B", "C")


def preflight(config: dict, feature_sets: dict, pool: str, allow_synthetic: bool = False) -> list[str]:
    """Stop with a clear message when the run cannot work; returns the notes to print. Checks the model type, the data files and the pool."""
    notes = []
    model_type = config["model"]["type"]
    try:
        create_model(model_type, dict(config["model"]["params"]))
    except Exception as exc:                                                       # unknown type, or parameters the model does not accept
        raise SystemExit(f"model.type {model_type!r} with the given model.params cannot be built: {exc}\n"
                         "Register a new model in src/models/model_factory.py (see ONBOARDING.md, 'Adding a model').") from exc
    train, test = resolve_path(config["paths"]["unsw_train"]), resolve_path(config["paths"]["unsw_test"])
    missing = [p for p in (train, test) if not p.exists()]
    if missing:
        if not allow_synthetic:
            raise SystemExit("Missing data file(s): " + ", ".join(str(p) for p in missing) + "\nFetch the UNSW-NB15 training and testing files with "
                             "`python scripts/download_datasets.py` (see README, 'Datasets'). To run on generated data only for a smoke test, add --allow-synthetic.")
        logger.warning("=" * 100 + "\nSYNTHETIC DATA: the UNSW-NB15 files are missing, so this run uses generated data. Its numbers are NOT results.\n" + "=" * 100)
        notes.append("SYNTHETIC DATA (--allow-synthetic): numbers are not results")
        return notes
    columns = set(pd.read_csv(train, nrows=0).columns)
    extra = sorted(set(feature_sets["feature_pool_full"]) - set(feature_sets["feature_pool"]))
    lacking = [c for c in extra if c not in columns]
    if lacking and POOLS[pool][0] != "base":
        raise SystemExit(f"Pool {pool} needs the full official files (42 feature columns); {train.name} lacks {lacking}.\n"
                         "The 36-column download only supports pool 40: rerun with --pool 40, or fetch the full files with `python scripts/download_datasets.py`.")
    notes.append(f"data: {train.name}, {test.name}; pools possible: " + ("40 only (the files lack the extra official columns)" if lacking else "48, 45, 40"))
    return notes


def apply_overrides(config: dict, run_name: str | None, out_dir: str | None) -> dict:
    """The effective config: project.run_name and, with out_dir, results/ and models_saved/ moved under it (the committed rankings are copied there first)."""
    cfg = copy.deepcopy(config)
    if run_name:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", run_name):
            raise SystemExit(f"--run-name {run_name!r}: use letters, digits, '_', '-' and '.' only")
        cfg.setdefault("project", {})["run_name"] = run_name
    if out_dir:
        out = Path(out_dir).resolve()
        source = resolve_path(cfg["paths"]["feature_ranking"].format(source=cfg["feature_selection"]["ranking_source"])).parent
        target = out / "results" / "rankings"
        target.mkdir(parents=True, exist_ok=True)
        for f in source.glob("feature_ranking_*"):
            if not (target / f.name).exists():
                shutil.copy2(f, target / f.name)
        cfg["paths"]["results_dir"] = str(out / "results")
        cfg["paths"]["models_dir"] = str(out / "models_saved")
        cfg["paths"]["feature_ranking"] = str(target / Path(cfg["paths"]["feature_ranking"]).name)
        cfg["paths"]["rating_dir"] = str(out / "results" / "rating")
        cfg["logging"]["log_file"] = str(out / "results" / "pipeline.log")      # not the repository's results/pipeline.log
    return cfg


def output_folders(config: dict) -> list[Path]:
    return [get_metrics_dir(config), get_plots_dir(config), get_models_dir(config)]


def check_output_free(config: dict, overwrite: bool) -> None:
    """Refuse to write into model folders that already hold results (unless --overwrite)."""
    busy = [d for d in output_folders(config) if d.exists() and any(p.is_file() for p in d.rglob("*"))]
    if busy and not overwrite:
        raise SystemExit("These folders already contain results:\n  " + "\n  ".join(str(d) for d in busy) +
                         f"\nNothing was changed. Use --run-name NAME to write to {model_folder(config)}__NAME instead, or --overwrite to replace them.")


def commands(config: dict, pool: str, steps: list[str]) -> list[list[str]]:
    """The pipeline commands of the chosen steps, in order."""
    name, label = POOLS[pool]
    model, py = config["model"]["type"], sys.executable
    cmds = []
    if "A" in steps:
        cmds.append([py, "pipelines/run_headline_seeds.py", "--pools", name])
    if "B" in steps:
        cmds += [[py, "pipelines/run_tier_study.py", "--model", model, "--pools", name, "--parts", "tiers", "pooled", "plots", "--no-plots"],
                 [py, "scripts/tier_summary.py", "--model", model, "--pools", label]]
    if "C" in steps:
        cmds.append([py, "scripts/explanation_stability_tiers.py", "--model", model, "--pools", label])
    if steps:
        cmds.append([py, "scripts/fill_model_template.py", "--model", model, "--pool", pool])
    return cmds


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--steps", nargs="*", choices=STEPS, default=list(STEPS), help="A headline, B tier study, C explanation stability (default: all three)")
    parser.add_argument("--config", help="a copy of configs/config.yaml with your model.type and model.params (default: configs/config.yaml, or $XAI_IDS_CONFIG)")
    parser.add_argument("--pool", choices=list(POOLS), default="48", help="feature pool: 48 (primary, needs the full official files), 40 or 45 (comparison pools)")
    parser.add_argument("--run-name", help="write to <model.type>__<run-name> folders (also project.run_name in the config)")
    parser.add_argument("--out-dir", help="write results/ and models_saved/ under this folder (e.g. results/_local_scratch/verify) instead of the repository's")
    parser.add_argument("--overwrite", action="store_true", help="replace results that already exist in the model's folders")
    parser.add_argument("--allow-synthetic", action="store_true", help="smoke test on generated data when the real files are missing (the numbers are not results)")
    args = parser.parse_args()

    config = load_config(args.config) if args.config else load_config()
    cfg = apply_overrides(config, args.run_name, args.out_dir)
    notes = preflight(cfg, load_feature_sets(), args.pool, args.allow_synthetic)
    check_output_free(cfg, args.overwrite)
    metrics_dir = get_metrics_dir(cfg)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    run_config = metrics_dir / "run_config.yaml"
    run_config.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")        # a record of the settings, and what every step loads
    env = dict(os.environ, **{CONFIG_ENV: str(run_config)})
    logger.info(f"model {cfg['model']['type']} (folder {model_folder(cfg)}), pool {args.pool}, steps {args.steps}; config for the steps: {run_config}")
    for note in notes:
        logger.info(note)
    for cmd in commands(cfg, args.pool, args.steps):
        logger.info("run: " + " ".join(Path(c).name if c == sys.executable else c for c in cmd))
        done = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env)
        if done.returncode:
            raise SystemExit(f"step failed (exit {done.returncode}): {' '.join(cmd[1:])}")
    print("\nDone. Written for", model_folder(cfg), ":")
    for d in output_folders(cfg):
        print(f"  {d}")
    print(f"  filled table: {metrics_dir / ('model_results_' + model_folder(cfg) + '.csv')}  (compare with results/REFERENCE_XGBOOST.csv)")


if __name__ == "__main__":
    main()
