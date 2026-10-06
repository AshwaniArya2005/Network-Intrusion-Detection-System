"""Where a flow's feature values sit among the training flows, overall and within each class (Task 5.5; protocol: results/03_novelty2_explanations.md, section `Source: narratives_protocol.md`).

`ClassReference` is fitted on the model's input matrix (numeric columns standardised, categorical columns integer codes) and the encoded training labels. For every numeric feature it keeps a
1,001-point quantile grid of all training flows and of each class's flows (resolution 0.1 percentage point); for every categorical feature the share of flows with each code, overall and per class.
It is saved with the model as an .npz (no pickle) so the dashboard can describe a flow relative to the class the model predicted.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

GRID = 1001


class ClassReference:
    def __init__(self, feature_names: list[str], class_names: list[str], categorical: list[str], q_all: np.ndarray, q_class: np.ndarray, cat_all: dict, cat_class: dict):
        self.feature_names, self.class_names, self.categorical = list(feature_names), list(class_names), list(categorical)
        self.q_all, self.q_class, self.cat_all, self.cat_class = q_all, q_class, cat_all, cat_class
        self._f = {f: i for i, f in enumerate(self.feature_names)}
        self._c = {c: i for i, c in enumerate(self.class_names)}

    @classmethod
    def fit(cls, X: np.ndarray, y: np.ndarray, class_names: list[str], feature_names: list[str], categorical: list[str]) -> "ClassReference":
        X, y = np.asarray(X, dtype=float), np.asarray(y)
        grid = np.linspace(0.0, 1.0, GRID)
        q_all, q_class = np.zeros((X.shape[1], GRID)), np.zeros((len(class_names), X.shape[1], GRID))
        cat_all, cat_class = {}, {}
        for j, name in enumerate(feature_names):
            if name in categorical:
                size = int(X[:, j].max()) + 2                                           # a code never seen in training (the "__unseen__" code) has share 0
                cat_all[name] = np.bincount(X[:, j].astype(int), minlength=size) / len(X)
                cat_class[name] = np.stack([np.bincount(X[y == k, j].astype(int), minlength=size) / max((y == k).sum(), 1) for k in range(len(class_names))])
                continue
            q_all[j] = np.quantile(X[:, j], grid)
            for k in range(len(class_names)):
                rows = X[y == k, j]
                q_class[k, j] = np.quantile(rows, grid) if len(rows) else q_all[j]
        return cls(feature_names, class_names, categorical, q_all, q_class, cat_all, cat_class)

    def _grid(self, feature: str, cls_name: str | None) -> np.ndarray:
        return self.q_all[self._f[feature]] if cls_name is None else self.q_class[self._c[cls_name], self._f[feature]]

    def share_below(self, feature: str, value: float, cls_name: str | None = None) -> float:
        """Share of the training flows (of the class, if given) whose value is strictly smaller (resolution 0.1 percentage point)."""
        return min(int(np.searchsorted(self._grid(feature, cls_name), value, side="left")), GRID - 1) / (GRID - 1)

    def share_above(self, feature: str, value: float, cls_name: str | None = None) -> float:
        """Share of the training flows (of the class, if given) whose value is strictly larger."""
        return (GRID - int(np.searchsorted(self._grid(feature, cls_name), value, side="right"))) / (GRID - 1) if value < self._grid(feature, cls_name)[-1] else 0.0

    def quartiles(self, feature: str, cls_name: str | None = None) -> tuple[float, float]:
        g = self._grid(feature, cls_name)
        return float(g[(GRID - 1) // 4]), float(g[3 * (GRID - 1) // 4])

    def category_share(self, feature: str, code: int, cls_name: str | None = None) -> float:
        table = self.cat_all[feature] if cls_name is None else self.cat_class[feature][self._c[cls_name]]
        return float(table[code]) if 0 <= code < len(table) else 0.0

    def save(self, path: str | Path) -> None:
        arrays = {"feature_names": np.array(self.feature_names), "class_names": np.array(self.class_names), "categorical": np.array(self.categorical, dtype="<U32"),
                  "q_all": self.q_all, "q_class": self.q_class}
        for name in self.categorical:
            arrays[f"catall__{name}"], arrays[f"catclass__{name}"] = self.cat_all[name], self.cat_class[name]
        np.savez_compressed(path, **arrays)

    @classmethod
    def load(cls, path: str | Path) -> "ClassReference":
        z = np.load(path, allow_pickle=False)
        categorical = [str(c) for c in z["categorical"]]
        return cls([str(f) for f in z["feature_names"]], [str(c) for c in z["class_names"]], categorical, z["q_all"], z["q_class"],
                   {c: z[f"catall__{c}"] for c in categorical}, {c: z[f"catclass__{c}"] for c in categorical})
