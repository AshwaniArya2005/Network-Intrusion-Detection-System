"""Task 5 Step 4: does the dashboard backend say what the pipeline says? (protocol: results/03_novelty2_explanations.md, section `Source: explanations_protocol.md`)

    python scripts/dashboard_end_to_end.py [--csv data/samples/sample_flows.csv]

Posts the sample flows to the FastAPI app (`dashboard.backend.main:app`, through the framework's own test client, the same request path as uvicorn) and compares, row by row, its prediction,
confidence, Unknown flag, narrative and top SHAP features with an independent computation from the SAME saved artifact: the saved model and preprocessor loaded directly, a separate
SHAPExplainer and a separate NarrativeGenerator. Every field must match exactly. Writes results/metrics/<model.type>/dashboard_end_to_end_<N>f.csv (one row per flow) and prints a summary.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import pandas as pd

from src.models.model_factory import create_scheme_model
from src.utils.config_loader import get_dashboard_paths, get_label_scheme, get_metrics_dir, load_config, resolve_path, scheme_tag
from src.xai.narrative_generator import NarrativeGenerator, standardised_value_statistics
from src.xai.shap_explainer import SHAPExplainer


def api_predictions(csv_path: Path) -> dict:
    from fastapi.testclient import TestClient
    from dashboard.backend.main import app
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        response = client.post("/predict", files={"file": (csv_path.name, csv_path.read_bytes(), "text/csv")})
    response.raise_for_status()
    return response.json()


def pipeline_predictions(config: dict, df: pd.DataFrame) -> list[dict]:
    """The same quantities computed without the dashboard: saved model + preprocessor loaded here, independent SHAP and narrative objects."""
    model_path, preprocessor_path = get_dashboard_paths(config)
    pre = joblib.load(preprocessor_path)    # the preprocessor this project trained and saved itself (models_saved/); joblib must never be pointed at untrusted files
    normal_index = list(pre.target_encoder.classes_).index(config["data"]["normal_category"])
    hierarchical = get_label_scheme(config)[2]
    model = create_scheme_model(config["model"]["type"], config["model"]["params"], hierarchical, normal_index)
    model.load(str(model_path))
    threshold_path = model_path.parent / f"open_set_{config['dashboard']['feature_set']}{scheme_tag(config)}.json"
    threshold = json.loads(threshold_path.read_text())["confidence_threshold"]
    X, _ = pre.transform(df)
    proba = model.predict_proba(X)
    pred, conf = proba.argmax(axis=1), proba.max(axis=1)
    unknown = conf < threshold
    shap_matrix = SHAPExplainer(model, pre.feature_list, config["xai"]["shap_background_samples"]).local_explanations(X, pred)
    means, stds = standardised_value_statistics(pre.numeric_features)
    generator = NarrativeGenerator(config["narrative"]["suggested_actions"])
    top_k, out = config["xai"]["top_k_features"], []
    for i in range(len(X)):
        label = pre.decode_target([pred[i]])[0]
        text = generator.generate(str(label), float(conf[i]), shap_matrix.iloc[i], pd.Series(X[i], index=pre.feature_list), means, stds, frozenset(pre.categorical_features),
                                  pre.label_encoders, top_k, bool(unknown[i]))
        top = SHAPExplainer.top_k(shap_matrix.iloc[i], k=top_k)
        out.append({"prediction": "Unknown" if unknown[i] else str(label), "confidence": round(float(conf[i]), 4), "is_unknown": bool(unknown[i]), "narrative": text,
                    "shap_top_features": [{"feature": f, "value": round(float(v), 4)} for f, v in top.items()]})
    return out


def compare(api: list[dict], own: list[dict]) -> pd.DataFrame:
    rows = []
    for i, (a, b) in enumerate(zip(api, own)):
        rows.append({"flow": i, "prediction": a["prediction"], "prediction_match": a["prediction"] == b["prediction"], "confidence_match": a["confidence"] == b["confidence"],
                     "unknown_match": a["is_unknown"] == b["is_unknown"], "narrative_match": a["narrative"] == b["narrative"],
                     "top_features_match": a["shap_top_features"] == b["shap_top_features"], "api_narrative": a["narrative"], "pipeline_narrative": b["narrative"]})
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", default="data/samples/sample_flows.csv")
    args = parser.parse_args()
    config = load_config()
    csv_path = resolve_path(args.csv)
    payload = api_predictions(csv_path)
    own = pipeline_predictions(config, pd.read_csv(io.BytesIO(csv_path.read_bytes())))
    table = compare(payload["predictions"], own)
    answers = resolve_path(args.csv.replace(".csv", "_answers.csv"))
    if answers.exists():
        truth = pd.read_csv(answers)["attack_cat"]
        table["true_attack_cat"] = truth.values[: len(table)]
    out = get_metrics_dir(config) / f"dashboard_end_to_end_{config['dashboard']['feature_set']}f.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out, index=False)
    checks = ["prediction_match", "confidence_match", "unknown_match", "narrative_match", "top_features_match"]
    print(f"{payload['n_rows']} flows posted to /predict; matches with the independent computation:")
    print(table[checks].mean().round(4).to_string())
    bad = table[~table[checks].all(axis=1)]
    print(f"flows with any difference: {len(bad)}; wrote {out}")


if __name__ == "__main__":
    main()
