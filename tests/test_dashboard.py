"""PredictionService + /predict endpoint, against a tiny model trained on synthetic data."""
from __future__ import annotations

import asyncio
import io
from types import SimpleNamespace

import joblib
import pandas as pd
import pytest
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.testclient import TestClient

from dashboard.backend import api
from dashboard.backend.prediction_service import PredictionService
from src.data_loader import make_synthetic_unsw
from src.models.model_factory import create_model, create_scheme_model
from src.preprocessing import Preprocessor
from src.utils.config_loader import get_dashboard_paths, load_config, load_feature_sets

SET_NAME = "15"


@pytest.fixture(scope="module")
def service(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("dash")
    config = load_config()
    config["paths"]["models_dir"] = str(tmp / "models")
    config["paths"]["feature_ranking"] = str(tmp / "no_ranking.csv")  # absent -> static pool order
    config["dashboard"]["feature_set"] = SET_NAME
    config["dashboard"]["max_rows"] = 50
    config["model"]["params"] = {"n_estimators": 20, "max_depth": 3, "random_state": 0}
    features = load_feature_sets()["feature_pool"][:15]

    df = make_synthetic_unsw(n_rows=400, seed=5)
    pre = Preprocessor(feature_list=features, target_column="attack_cat").fit(df)
    X, y = pre.transform(df)
    model_path, pre_path = get_dashboard_paths(config)
    model_path.parent.mkdir(parents=True)
    create_model("xgboost", config["model"]["params"]).fit(X, y).save(str(model_path))
    joblib.dump(pre, pre_path)
    svc = PredictionService(config)
    svc.df = df
    return svc


@pytest.fixture
def client(service, monkeypatch):
    monkeypatch.setattr(api, "get_prediction_service", lambda: service)
    app = FastAPI()
    app.include_router(api.router)
    return TestClient(app)


def _csv(df: pd.DataFrame) -> dict:
    return {"file": ("flows.csv", df.to_csv(index=False).encode(), "text/csv")}


def test_narrative_uses_scaled_value_as_zscore_once(service, monkeypatch):
    """A flow whose `rate` is 3 training-stds above the training mean must read "extremely
    high". The service used to z-score the already-standardised value against the raw mean/std
    again, so nearly everything read "typical"/"reduced"."""
    scale = service.preprocessor.scaler
    i = service.preprocessor.numeric_features.index("rate")
    row = service.df.head(1).copy()
    row["rate"] = scale.mean_[i] + 3 * scale.scale_[i]

    only_rate = pd.DataFrame(0.0, index=[0], columns=service.features)
    only_rate["rate"] = 1.0
    monkeypatch.setattr(service.explainer, "local_explanations", lambda X, idx: only_rate)

    narrative = service.predict(row)[0]["narrative"]
    assert "extremely high packet rate" in narrative


def test_predict_endpoint_returns_predictions(client, service):
    res = client.post("/predict", files=_csv(service.df.head(3)))
    assert res.status_code == 200
    body = res.json()
    assert body["n_rows"] == 3 and len(body["predictions"]) == 3
    assert {"prediction", "confidence", "narrative", "shap_top_features"} <= set(body["predictions"][0])


def test_predict_endpoint_names_missing_columns(client, service):
    res = client.post("/predict", files=_csv(service.df.head(2).drop(columns=["rate", "proto"])))
    assert res.status_code == 400
    assert "rate" in res.json()["detail"] and "proto" in res.json()["detail"]


def test_predict_endpoint_rejects_oversize_file_and_too_many_rows(client, service, monkeypatch):
    monkeypatch.setattr(api, "MAX_UPLOAD_BYTES", 50)
    assert client.post("/predict", files=_csv(service.df.head(3))).status_code == 400
    monkeypatch.undo()
    monkeypatch.setattr(api, "get_prediction_service", lambda: service)
    assert client.post("/predict", files=_csv(service.df.head(51))).status_code == 400


def test_predict_endpoint_rejects_non_csv_and_missing_filename(client):
    assert client.post("/predict", files={"file": ("flows.txt", b"a,b", "text/plain")}).status_code == 400
    nameless = UploadFile(file=io.BytesIO(b"a,b\n1,2\n"), filename=None)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(api.predict(nameless))
    assert exc.value.status_code == 400


def test_predict_endpoint_requires_base_columns_of_engineered_features(monkeypatch):
    """A feature set with pkt_ratio but not spkts still needs spkts: a CSV without it must be a
    400 naming it, not silently different features."""
    stub = SimpleNamespace(config={"dashboard": {"max_rows": 50}},
                           preprocessor=Preprocessor(feature_list=["rate", "pkt_ratio"]))
    monkeypatch.setattr(api, "get_prediction_service", lambda: stub)
    app = FastAPI()
    app.include_router(api.router)
    flows = pd.DataFrame({"rate": [1.0], "dpkts": [2.0]})
    res = TestClient(app).post("/predict", files=_csv(flows))
    assert res.status_code == 400 and "spkts" in res.json()["detail"]


def test_service_loads_and_explains_a_hierarchical_model(tmp_path):
    config = load_config()
    config["data"]["label_scheme"] = "hierarchical"
    config["paths"].update(models_dir=str(tmp_path / "models"), feature_ranking=str(tmp_path / "none_{source}.csv"))
    config["dashboard"].update(feature_set="15")
    config["model"]["params"] = {"n_estimators": 10, "max_depth": 3, "random_state": 0}
    features = load_feature_sets()["feature_pool"][:15]

    df = make_synthetic_unsw(n_rows=500, seed=6)
    pre = Preprocessor(feature_list=features, target_column="attack_cat").fit(df)
    X, y = pre.transform(df)
    normal_index = list(pre.target_encoder.classes_).index("Normal")
    model_path, pre_path = get_dashboard_paths(config)
    model_path.parent.mkdir(parents=True)
    create_scheme_model("xgboost", config["model"]["params"], True, normal_index).fit(X, y).save(str(model_path))
    joblib.dump(pre, pre_path)

    out = PredictionService(config).predict(df.head(5))
    assert len(out) == 5 and all(r["shap_top_features"] for r in out)
