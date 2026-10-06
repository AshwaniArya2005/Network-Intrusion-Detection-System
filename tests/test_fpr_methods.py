"""Task 2.7 methods, checked by hand."""
import numpy as np
import pytest

from src.fpr_methods import (
    apply_temperature, diverse_selection, em_gate, em_prior, entropy, entropy_selection, fit_temperature, mix_selection, prior_correct,
    pseudo_labels, random_selection, weighted_prior,
)


def test_temperature_one_keeps_probabilities_and_larger_temperature_flattens_them():
    p = np.array([[0.7, 0.2, 0.1], [0.5, 0.25, 0.25]])
    assert np.allclose(apply_temperature(p, 1.0), p)
    flat = apply_temperature(p, 3.0)
    assert np.allclose(flat.sum(axis=1), 1) and (flat.max(axis=1) < p.max(axis=1)).all()
    assert np.allclose(apply_temperature(p, 2.0)[0], np.sqrt(p[0]) / np.sqrt(p[0]).sum())      # p ** (1/2), renormalised, by hand


def test_fit_temperature_recovers_overconfidence():
    rng = np.random.default_rng(0)
    true = rng.dirichlet([2, 2, 2], size=4000)
    y = np.array([rng.choice(3, p=row) for row in true])                  # labels drawn from the calibrated probabilities
    sharp = apply_temperature(true, 0.5)                                  # an over-confident model
    assert 1.8 < fit_temperature(sharp, y) < 2.2                          # undoing T = 0.5 needs T = 2
    assert 0.9 < fit_temperature(true, y) < 1.1                           # already calibrated


def test_weighted_prior_and_correction_by_hand():
    y, w = np.array([0, 0, 1, 2]), np.array([1.0, 1.0, 2.0, 4.0])
    prior = weighted_prior(y, w, 3)                                      # class 0: 1 + 1, class 1: 2, class 2: 4, total 8
    assert np.allclose(prior, [2 / 8, 2 / 8, 4 / 8])
    p = np.array([[0.5, 0.5]])
    assert np.allclose(prior_correct(p, np.array([0.8, 0.2]), np.array([0.5, 0.5])), [[0.8, 0.2]])      # weights 0.5*0.8 : 0.5*0.2
    assert np.allclose(prior_correct(p, np.array([0.5, 0.5]), np.array([0.5, 0.5])), p)


def test_em_prior_recovers_the_shifted_class_shares():
    rng = np.random.default_rng(1)
    pi_model, pi_test = np.array([0.5, 0.5]), np.array([0.8, 0.2])
    n = 20000
    y = rng.choice(2, size=n, p=pi_test)
    mean = np.where(y == 1, 1.0, -1.0)
    x = rng.normal(mean, 1.0)
    # the model's posterior under the balanced prior for two unit-variance Gaussians at -1 / +1: sigmoid(2x)
    p1 = 1 / (1 + np.exp(-2 * x))
    proba = np.column_stack([1 - p1, p1])
    estimate = em_prior(proba, pi_model)
    assert estimate.sum() == pytest.approx(1.0) and abs(estimate[0] - 0.8) < 0.02
    assert np.allclose(em_prior(proba[: n // 2], np.array([0.5, 0.5]), max_iter=1)[0], prior_correct(proba[: n // 2], pi_model, pi_model).mean(axis=0)[0])   # one iteration


def test_em_gate_passes_when_the_probabilities_are_informative_and_fails_when_they_are_not():
    rng = np.random.default_rng(2)
    y = rng.choice(3, size=6000, p=[0.5, 0.3, 0.2])
    informative = np.eye(3)[y] * 0.8 + 0.2 / 3
    pi_model = np.array([1 / 3, 1 / 3, 1 / 3])
    assert em_gate(informative, y, pi_model)["passes"] is True
    useless = np.tile(pi_model, (len(y), 1))                              # probabilities that ignore the features: EM cannot move
    result = em_gate(useless, y, pi_model)
    assert result["passes"] is False and result["em_l1_error"] == pytest.approx(result["model_prior_l1_distance"])


def test_pseudo_labels_use_the_threshold_and_the_argmax():
    p = np.array([[0.95, 0.05], [0.6, 0.4], [0.1, 0.9]])
    mask, labels = pseudo_labels(p, 0.9)
    assert mask.tolist() == [True, False, True] and labels.tolist() == [0, 0, 1]


def test_entropy_and_selections_by_hand():
    p = np.array([[0.5, 0.5], [0.9, 0.1], [0.99, 0.01], [0.6, 0.4]])
    assert entropy(p)[0] == pytest.approx(np.log(2))
    assert entropy_selection(p, 2).tolist() == [0, 3]                                  # the two most uncertain rows
    pick = random_selection(100, 10, seed=3)
    assert len(set(pick.tolist())) == 10 and np.array_equal(pick, random_selection(100, 10, seed=3))


def test_diverse_selection_spreads_over_clusters_and_mix_has_the_declared_split():
    rng = np.random.default_rng(4)
    centres = np.array([[0, 0], [10, 0], [0, 10], [10, 10]], dtype=float)
    X = np.vstack([c + rng.normal(0, 0.1, size=(50, 2)) for c in centres])
    pick = diverse_selection(X, 4, seed=0)
    assert len(pick) == 4 and sorted((pick // 50).tolist()) == [0, 1, 2, 3]            # one row per cluster
    assert len(diverse_selection(X, 300)) == len(X)                                    # a budget larger than the pool takes everything
    proba = np.tile([0.9, 0.1], (len(X), 1))
    proba[:3] = [0.5, 0.5]
    mixed = mix_selection(proba, X, 6, seed=0)
    assert len(set(mixed.tolist())) == 6 and {0, 1, 2} <= set(mixed.tolist())          # ceil(6/2) = 3 most uncertain rows + 3 diverse ones
