"""Feature-vector overlap between classes: exact/near twins and the best-possible accuracy.

Method (all in-sample, on whichever rows are passed in):
  - A *feature vector* is a row's values over `features` (hashed).
  - Exact twin: a vector that also occurs under another class.
  - Near twin: a distinct vector with a vector of another class within L-inf distance r after
    log1p (numeric columns, clipped at 0), standardisation over the distinct vectors, with
    categoricals required to match exactly. Distance 0 (exact twins) counts.
  - Best-possible accuracy: a deterministic classifier assigns ONE label per distinct vector,
    so the ceiling is sum over vectors of (max class count) / N. Coarser labels raise it
    mechanically: it measures information a label scheme discards, not which scheme is right.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from src.preprocessing import CATEGORICAL_FEATURES

NEAR_THRESHOLDS = (0.05, 0.1, 0.25)


def vector_ids(df: pd.DataFrame, features: list[str]) -> np.ndarray:
    return pd.util.hash_pandas_object(df[features], index=False).to_numpy()


def best_possible_accuracy(df: pd.DataFrame, features: list[str], label_col: str, dedup_pairs: bool = False) -> float:
    """Ceiling accuracy for `label_col`. With `dedup_pairs`, each distinct (vector, label) pair
    counts once (removes duplicate-count weighting); otherwise duplicates are kept."""
    pairs = pd.DataFrame({"vec": vector_ids(df, features), "label": df[label_col].to_numpy()})
    if dedup_pairs:
        pairs = pairs.drop_duplicates()
    counts = pairs.groupby(["vec", "label"]).size()
    return float(counts.groupby(level="vec").max().sum() / len(pairs))


def largest_multilabel_vector(df: pd.DataFrame, features: list[str], label_col: str) -> dict:
    """Worked example: the feature vector shared by the most rows across more than one label."""
    ids = vector_ids(df, features)
    counts = pd.DataFrame({"vec": ids, "label": df[label_col].to_numpy()}).groupby(["vec", "label"]).size()
    multi = counts.groupby(level="vec").filter(lambda g: len(g) > 1)
    if multi.empty:
        return {}
    vec = multi.groupby(level="vec").sum().idxmax()
    row = df.iloc[int(np.flatnonzero(ids == vec)[0])][features]
    return {"vector": row.to_dict(), "label_counts": multi.loc[vec].to_dict()}


def normal_overlap_floor(train: pd.DataFrame, test: pd.DataFrame, features: list[str], label_col: str = "attack_cat", normal: str = "Normal") -> dict:
    """How much of the Normal-flow false-positive rate is forced by feature-vector overlap (exact twins), as shares of the test Normal rows.

    within_test_*: counted among the test file's own rows (what a model that had seen the test labels could not escape).
      attack_twin   the Normal row's vector also occurs on an attack row of the test file
      forced        its vector has strictly more attack rows than Normal rows (ties count as Normal, so this is a lower bound)
    from_train_*: what the training labels say about the test Normal row's vector.
      seen_attack_only / seen_attack_majority / seen_normal_majority / unseen"""
    test_ids = vector_ids(test, features)
    is_attack = (test[label_col] != normal).to_numpy()
    counts = pd.DataFrame({"vec": test_ids, "attack": is_attack}).groupby("vec")["attack"].agg(n_attack="sum", n="size")
    counts["n_normal"] = counts["n"] - counts["n_attack"]
    mine = counts.reindex(test_ids[~is_attack])
    train_ids = vector_ids(train, features)
    tr = pd.DataFrame({"vec": train_ids, "attack": (train[label_col] != normal).to_numpy()}).groupby("vec")["attack"].agg(n_attack="sum", n="size")
    tr["n_normal"] = tr["n"] - tr["n_attack"]
    seen = tr.reindex(test_ids[~is_attack])
    unseen = seen["n"].isna().to_numpy()
    n_attack, n_normal = seen["n_attack"].fillna(0).to_numpy(), seen["n_normal"].fillna(0).to_numpy()
    return {"n_test_normal": int(len(mine)),
            "within_test_attack_twin": float((mine["n_attack"] > 0).mean()),
            "within_test_forced": float((mine["n_attack"] > mine["n_normal"]).mean()),
            "from_train_unseen": float(unseen.mean()),
            "from_train_seen_attack_only": float(((n_attack > 0) & (n_normal == 0)).mean()),
            "from_train_seen_attack_majority": float((n_attack > n_normal).mean()),
            "from_train_seen_normal_majority": float((n_normal >= n_attack)[~unseen].sum() / len(mine))}


def exact_twin_matrix(df: pd.DataFrame, features: list[str], label_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(rows_pct, vectors_pct): for each class A (row) and each other class B (column, plus
    "any_other"), the % of A's rows / of A's distinct vectors that also occur under B."""
    ids = vector_ids(df, features)
    labels = df[label_col].to_numpy()
    classes = sorted(set(labels))
    members = {c: ids[labels == c] for c in classes}
    sets = {c: set(members[c]) for c in classes}
    cols = classes + ["any_other"]
    rows_pct = pd.DataFrame(np.nan, index=classes, columns=cols)
    vecs_pct = pd.DataFrame(np.nan, index=classes, columns=cols)
    for a in classes:
        rows_a, uniq_a = members[a], np.unique(members[a])
        others = set().union(*(sets[b] for b in classes if b != a)) if len(classes) > 1 else set()
        for b in classes:
            if b != a:
                rows_pct.loc[a, b] = 100 * np.isin(rows_a, list(sets[b])).mean()
                vecs_pct.loc[a, b] = 100 * np.isin(uniq_a, list(sets[b])).mean()
        rows_pct.loc[a, "any_other"] = 100 * np.isin(rows_a, list(others)).mean()
        vecs_pct.loc[a, "any_other"] = 100 * np.isin(uniq_a, list(others)).mean()
    return rows_pct.round(2), vecs_pct.round(2)


def _embedding(df: pd.DataFrame, features: list[str]) -> np.ndarray:
    num = [f for f in features if f not in CATEGORICAL_FEATURES]
    cat = [f for f in features if f in CATEGORICAL_FEATURES]
    x = np.log1p(df[num].astype(float).clip(lower=0)).to_numpy()
    sd = x.std(axis=0)
    x = (x - x.mean(axis=0)) / np.where(sd > 0, sd, 1.0)
    codes = np.column_stack([pd.factorize(df[c])[0] for c in cat]) * 1000.0 if cat else np.empty((len(df), 0))
    return np.hstack([x, codes])  # a categorical mismatch is >= 1000 away: never "near"


def near_twin_rates(df: pd.DataFrame, features: list[str], label_col: str,
                    thresholds: tuple[float, ...] = NEAR_THRESHOLDS) -> pd.DataFrame:
    """Per class: % of its distinct vectors with a vector of ANOTHER class within each L-inf
    distance threshold (see module docstring for the transform)."""
    pairs = df[features + [label_col]].assign(vec=vector_ids(df, features)).drop_duplicates(["vec", label_col])
    emb = _embedding(pairs, features)
    labels = pairs[label_col].to_numpy()
    out = {}
    for a in sorted(set(labels)):
        pts = emb[labels == a]  # one row per distinct (vector, label) pair
        others = emb[labels != a]
        if len(others) == 0:
            continue
        dist, _ = cKDTree(others).query(pts, p=np.inf, distance_upper_bound=max(thresholds) + 1e-9, workers=-1)
        out[a] = {f"within_{t}": 100 * float((dist <= t + 1e-12).mean()) for t in thresholds} | {"n_distinct_vectors": len(pts)}
    return pd.DataFrame(out).T.round(2)


def analyse(df: pd.DataFrame, features: list[str], label_cols: dict[str, str], near: bool = True) -> dict:
    """Run every overlap measure for each named label column. Returns
    {"ceilings": DataFrame, "twin_rows": {name: df}, "twin_vectors": {name: df}, "near": {name: df},
     "example": {name: dict}}."""
    ceilings = pd.DataFrame([{
        "label_scheme": name, "n_classes": df[col].nunique(),
        "best_possible_accuracy_dups_kept": round(best_possible_accuracy(df, features, col), 4),
        "best_possible_accuracy_pairs_deduped": round(best_possible_accuracy(df, features, col, dedup_pairs=True), 4),
    } for name, col in label_cols.items()])
    out = {"ceilings": ceilings, "twin_rows": {}, "twin_vectors": {}, "near": {}, "example": {}}
    for name, col in label_cols.items():
        out["twin_rows"][name], out["twin_vectors"][name] = exact_twin_matrix(df, features, col)
        out["example"][name] = largest_multilabel_vector(df, features, col)
        if near:
            out["near"][name] = near_twin_rates(df, features, col)
    return out


def render_markdown(result: dict, header: str) -> str:
    """Short markdown summary of an `analyse` result."""
    lines = [f"# Overlap analysis", "", header, "", "## Best-possible accuracy", "",
             "```", result["ceilings"].to_string(index=False), "```", ""]
    for name, tbl in result["twin_rows"].items():
        lines += [f"## Exact twins, label set '{name}' (% of rows / % of distinct vectors with a twin in another class)", "",
                  "```", pd.concat({"rows_pct": tbl["any_other"], "vectors_pct": result["twin_vectors"][name]["any_other"]},
                                  axis=1).to_string(), "```", ""]
        ex = result["example"][name]
        if ex:
            lines += [f"Largest multi-label vector ('{name}'): label counts {ex['label_counts']}", ""]
        if name in result["near"]:
            lines += ["Near twins (% of distinct vectors with another class within L-inf distance r):", "```",
                      result["near"][name].to_string(), "```", ""]
    return "\n".join(lines)
