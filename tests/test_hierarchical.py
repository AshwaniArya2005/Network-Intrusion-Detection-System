"""HierarchicalModel: persistence, sample weights, SHAP index mapping, factory."""
import numpy as np
import pytest

from src.models.hierarchical_model import HierarchicalModel
from src.models.model_factory import create_model, create_scheme_model
from src.xai.shap_explainer import SHAPExplainer

N_CLASSES, NORMAL = 9, 1
PARAMS = {"n_estimators": 10, "max_depth": 3, "random_state": 0}


@pytest.fixture(scope="module")
def data():
    rng = np.random.default_rng(0)
    y = rng.integers(0, N_CLASSES, 1800)
    X = rng.normal(size=(1800, 6)) + np.eye(N_CLASSES)[y][:, :6] * 2 + (y[:, None] / 3.0)
    return X, y


@pytest.fixture(scope="module")
def model(data):
    X, y = data
    return create_scheme_model("xgboost", PARAMS, True, NORMAL).fit(X, y)


def test_factory_builds_hierarchical_only_for_the_hierarchical_scheme(model):
    assert isinstance(model, HierarchicalModel)
    assert not isinstance(create_scheme_model("xgboost", PARAMS, False), HierarchicalModel)
    with pytest.raises(ValueError):
        create_scheme_model("xgboost", PARAMS, True)  # needs the Normal index


def test_save_load_round_trip_gives_identical_probabilities(model, data, tmp_path):
    X, _ = data
    model.save(str(tmp_path / "hier.json"))
    assert (tmp_path / "hier" / "meta.json").exists()
    restored = create_scheme_model("xgboost", PARAMS, True, NORMAL).load(str(tmp_path / "hier.json"))
    np.testing.assert_allclose(restored.predict_proba(X), model.predict_proba(X), atol=1e-6)
    assert list(restored.attack_classes) == list(model.attack_classes) and restored.n_classes == N_CLASSES


def test_probabilities_are_a_valid_distribution(model, data):
    proba = model.predict_proba(data[0])
    assert proba.shape == (len(data[0]), N_CLASSES) and np.allclose(proba.sum(axis=1), 1.0, atol=1e-5)


def test_given_sample_weight_is_used_else_each_stage_balances(data):
    X, y = data
    seen = []

    class Spy:
        def __init__(self):
            self.inner = create_model("xgboost", PARAMS)

        def fit(self, X, y, sample_weight=None):
            seen.append(sample_weight)
            self.inner.fit(X, y, sample_weight=sample_weight)
            return self

        def __getattr__(self, name):
            return getattr(self.inner, name)

    given = np.full(len(y), 2.0)
    HierarchicalModel(Spy, NORMAL).fit(X, y, sample_weight=given)
    assert (seen[0] == 2.0).all() and (seen[1] == 2.0).all() and len(seen[1]) == (y != NORMAL).sum()
    seen.clear()
    HierarchicalModel(Spy, NORMAL).fit(X, y)
    assert len(np.unique(seen[0])) > 1 and len(np.unique(seen[1])) > 1  # balanced per stage


def test_explanation_for_a_class_index_above_seven_uses_the_right_stage2_class(model, data):
    """The composed class 8 is stage-2 class 7 (attack classes skip the Normal index 1)."""
    X, y = data
    names = [f"f{i}" for i in range(X.shape[1])]
    explainer = SHAPExplainer(model, names, background_samples=50)
    rows = X[y == 8][:20]
    got = explainer.local_explanations(rows, [8] * len(rows)).to_numpy()

    stage2 = SHAPExplainer(model.stage2, names, background_samples=50)
    family = int(np.searchsorted(model.attack_classes, 8))
    assert family == 7 != 8
    np.testing.assert_allclose(got, stage2.local_explanations(rows, [family] * len(rows)).to_numpy(), atol=1e-6)
    wrong = stage2.local_explanations(rows, [6] * len(rows)).to_numpy()
    assert not np.allclose(got, wrong)

    # Normal is explained by stage 1 (class 0 = "not attack"), never by a stage-2 column.
    normal_rows = X[y == NORMAL][:10]
    stage1 = SHAPExplainer(model.stage1, names, background_samples=50)
    np.testing.assert_allclose(explainer.local_explanations(normal_rows, [NORMAL] * 10).to_numpy(),
                               stage1.local_explanations(normal_rows, [0] * 10).to_numpy(), atol=1e-6)


def test_unknown_class_index_is_rejected_and_global_shap_has_one_array_per_class(model, data):
    X, _ = data
    explainer = SHAPExplainer(model, [f"f{i}" for i in range(6)], background_samples=50)
    per_class = explainer.compute_shap_values(X[:60], max_samples=60)
    assert len(per_class) == N_CLASSES and per_class[0].shape == (60, 6)
    with pytest.raises(ValueError):
        explainer.local_explanations(X[:2], [N_CLASSES + 3, 0])
