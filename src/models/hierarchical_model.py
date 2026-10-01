"""Two-stage classifier: stage 1 attack vs. normal, stage 2 attack family.

Wraps any BaseModel factory. The composed class probabilities are
P(normal) = p1(normal) and P(c) = p1(attack) * p2(c | attack), so predict/predict_proba,
the open-set wrapper's confidence and every metric work unchanged on the (n, n_classes)
matrix. Used by the "hierarchical" label scheme (configs/config.yaml `data.label_schemes`).

Index spaces: the composed output uses the label encoder's class indexes (0..n_classes-1);
stage 1 is binary (0 = normal, 1 = attack); stage 2 uses the rank of a class within
`attack_classes` (0..len(attack_classes)-1). Never mix them: SHAPExplainer maps between them.

Persistence: `save(path)` writes a directory (`path` without its suffix) holding stage1/stage2
artifacts and meta.json (normal_index, attack_classes, n_classes); `load(path)` reads it back.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from src.models.base_model import BaseModel
from src.preprocessing import balanced_sample_weight


class HierarchicalModel(BaseModel):
    def __init__(self, make_model: Callable[[], BaseModel], normal_index: int, artifact_suffix: str = ".json"):
        self._make = make_model
        self.normal_index = normal_index
        self.artifact_suffix = artifact_suffix
        self.stage1 = make_model()
        self.stage2 = make_model()
        self.attack_classes: np.ndarray = np.array([], dtype=int)
        self.n_classes = 0

    def fit(self, X: np.ndarray, y: np.ndarray, sample_weight: np.ndarray | None = None) -> "HierarchicalModel":
        """`sample_weight` (per row of X) is used by both stages when given; otherwise each stage
        gets its own square-rooted balanced weights."""
        is_attack = y != self.normal_index
        self.n_classes = int(y.max()) + 1
        self.attack_classes = np.unique(y[is_attack])
        y_family = np.searchsorted(self.attack_classes, y[is_attack])
        w1 = sample_weight if sample_weight is not None else balanced_sample_weight(is_attack.astype(int))
        w2 = sample_weight[is_attack] if sample_weight is not None else balanced_sample_weight(y_family)
        self.stage1.fit(X, is_attack.astype(int), sample_weight=w1)
        self.stage2.fit(X[is_attack], y_family, sample_weight=w2)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        p_attack = self.stage1.predict_proba(X)[:, 1]
        family = self.stage2.predict_proba(X)
        proba = np.zeros((len(X), self.n_classes))
        proba[:, self.normal_index] = 1 - p_attack
        proba[:, self.attack_classes] = p_attack[:, None] * family
        return proba

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.argmax(self.predict_proba(X), axis=1)

    def get_feature_importance(self) -> np.ndarray:
        return (self.stage1.get_feature_importance() + self.stage2.get_feature_importance()) / 2

    def save(self, path: str) -> None:
        directory = Path(path).with_suffix("")
        directory.mkdir(parents=True, exist_ok=True)
        self.stage1.save(str(directory / f"stage1{self.artifact_suffix}"))
        self.stage2.save(str(directory / f"stage2{self.artifact_suffix}"))
        (directory / "meta.json").write_text(json.dumps({
            "normal_index": int(self.normal_index), "attack_classes": [int(c) for c in self.attack_classes],
            "n_classes": int(self.n_classes), "artifact_suffix": self.artifact_suffix}))

    def load(self, path: str) -> "HierarchicalModel":
        directory = Path(path).with_suffix("")
        meta = json.loads((directory / "meta.json").read_text())
        self.normal_index = meta["normal_index"]
        self.attack_classes = np.array(meta["attack_classes"], dtype=int)
        self.n_classes = meta["n_classes"]
        self.artifact_suffix = meta["artifact_suffix"]
        self.stage1 = self._make().load(str(directory / f"stage1{self.artifact_suffix}"))
        self.stage2 = self._make().load(str(directory / f"stage2{self.artifact_suffix}"))
        return self

    @property
    def underlying_model(self) -> Any:
        """Stage 2 only; explain a hierarchical model with SHAPExplainer, which handles both stages."""
        return self.stage2.underlying_model
