# tests/test_fair_engine.py
# The FAIR engine is the part of this project a reviewer is most likely to
# check the maths on, so these tests pin it against closed-form results
# rather than against previously observed output.

import math

import numpy as np
import pytest

from src.risk_quantification.fair_engine import (
    compute_rosi,
    format_currency,
    run_fair_simulation,
    seed_for,
)
from src.risk_quantification.scenarios import SCENARIOS

SEED = 20260921


def lognormal_params(loss_low, loss_high):
    """The mu and sigma the engine derives from a 90% confidence interval."""
    mu    = (math.log(loss_low) + math.log(loss_high)) / 2
    sigma = (math.log(loss_high) - math.log(loss_low)) / (2 * 1.645)
    return mu, sigma


def analytic_ale(loss_low, loss_high, freq_low, freq_high):
    """
    Closed-form expected annual loss for a compound Poisson model.

    E[sum of N log-normal draws] = E[N] * E[X] = lambda * exp(mu + sigma^2/2)
    """
    mu, sigma = lognormal_params(loss_low, loss_high)
    lam       = (freq_low + freq_high) / 2
    return lam * math.exp(mu + sigma ** 2 / 2)


@pytest.mark.parametrize("key", list(SCENARIOS))
def test_ale_matches_analytic_mean(key):
    """Simulated ALE lands within 3% of lambda * exp(mu + sigma^2/2)."""
    sc       = SCENARIOS[key]
    result   = run_fair_simulation(
        sc["loss_low"], sc["loss_high"], sc["freq_low"], sc["freq_high"],
        seed=seed_for(sc["id"]),
    )
    expected = analytic_ale(
        sc["loss_low"], sc["loss_high"], sc["freq_low"], sc["freq_high"]
    )
    relative_error = abs(result["ale"] - expected) / expected
    assert relative_error < 0.03, (
        f"{key}: simulated ALE {result['ale']:,.0f} vs analytic "
        f"{expected:,.0f} — {relative_error:.2%} off"
    )


@pytest.mark.parametrize("key", list(SCENARIOS))
def test_percentiles_are_ordered(key):
    """median <= p90 <= p95 <= p99, and the ALE is positive."""
    sc = SCENARIOS[key]
    r  = run_fair_simulation(
        sc["loss_low"], sc["loss_high"], sc["freq_low"], sc["freq_high"],
        seed=seed_for(sc["id"]),
    )
    assert r["ale"] > 0
    assert r["median"] <= r["percentile_90"] <= r["percentile_95"] <= r["percentile_99"]


def test_zero_frequency_produces_no_loss():
    """A scenario that never happens costs nothing, and does not divide by zero."""
    r = run_fair_simulation(
        loss_low=500_000, loss_high=8_000_000,
        freq_low=0, freq_high=0, n=1_000, seed=SEED,
    )
    assert r["ale"] == 0.0
    assert r["median"] == 0.0
    assert r["percentile_99"] == 0.0
    assert r["prob_over_1m"] == 0.0
    assert len(r["annual_losses"]) == 1_000
    assert np.all(r["annual_losses"] == 0)


def test_losses_are_summed_not_multiplied():
    """
    Each event in a year is an independent draw.

    If the engine multiplied one magnitude by the event count, every year with
    N events would be an exact multiple of a single draw. Summing independent
    draws produces a much lighter tail, so this pins the p99-to-mean ratio
    below what the multiplicative model gives for the same inputs.
    """
    kwargs = dict(loss_low=500_000, loss_high=8_000_000,
                  freq_low=0.5, freq_high=3.0, n=100_000)
    summed = run_fair_simulation(seed=SEED, **kwargs)

    rng   = np.random.default_rng(SEED)
    mu, sigma = lognormal_params(kwargs["loss_low"], kwargs["loss_high"])
    lam   = (kwargs["freq_low"] + kwargs["freq_high"]) / 2
    multiplied = (rng.poisson(lam, kwargs["n"])
                  * rng.lognormal(mu, sigma, kwargs["n"]))

    summed_ratio     = summed["percentile_99"] / summed["ale"]
    multiplied_ratio = np.percentile(multiplied, 99) / np.mean(multiplied)
    assert summed_ratio < multiplied_ratio


def test_seed_makes_runs_reproducible():
    """The same seed gives the same numbers; a different seed does not."""
    kwargs = dict(loss_low=200_000, loss_high=5_000_000,
                  freq_low=0.5, freq_high=2.0, n=10_000)
    a = run_fair_simulation(seed=SEED, **kwargs)
    b = run_fair_simulation(seed=SEED, **kwargs)
    c = run_fair_simulation(seed=SEED + 1, **kwargs)

    assert a["ale"] == b["ale"]
    assert np.array_equal(a["annual_losses"], b["annual_losses"])
    assert a["ale"] != c["ale"]


def test_seed_for_is_distinct_per_scenario():
    """Every scenario gets its own deterministic seed."""
    seeds = [seed_for(sc["id"]) for sc in SCENARIOS.values()]
    assert len(set(seeds)) == len(SCENARIOS)
    assert seed_for(3) == seed_for(3)


def test_higher_frequency_raises_ale():
    """More events a year means more expected loss, all else equal."""
    base = dict(loss_low=500_000, loss_high=8_000_000, n=20_000, seed=SEED)
    low  = run_fair_simulation(freq_low=0.5, freq_high=1.0, **base)
    high = run_fair_simulation(freq_low=3.0, freq_high=4.0, **base)
    assert high["ale"] > low["ale"]


# ─────────────────────────────────────────────────────────────
# ROSI
# ─────────────────────────────────────────────────────────────
def test_rosi_matches_the_documented_formula():
    """rosi = (risk_reduction - control_cost) / control_cost."""
    econ = compute_rosi(ale=1_000_000, control_cost=100_000,
                        control_effectiveness=0.70)
    assert econ["residual_ale"] == pytest.approx(300_000)
    assert econ["risk_reduction"] == pytest.approx(700_000)
    assert econ["rosi"] == pytest.approx(6.0)
    assert econ["rosi_pct"] == pytest.approx(600.0)


def test_rosi_goes_negative_when_controls_cost_more_than_they_save():
    econ = compute_rosi(ale=100_000, control_cost=200_000,
                        control_effectiveness=0.60)
    assert econ["rosi"] < 0


def test_rosi_handles_zero_control_cost():
    """A free control should not raise ZeroDivisionError."""
    assert compute_rosi(ale=100_000, control_cost=0,
                        control_effectiveness=0.5)["rosi"] == 0.0


def test_control_effectiveness_stays_within_the_documented_band():
    """Every scenario documents an effectiveness assumption between 0.60 and 0.80."""
    for key, sc in SCENARIOS.items():
        assert 0.60 <= sc["control_effectiveness"] <= 0.80, key


# ─────────────────────────────────────────────────────────────
def test_format_currency():
    assert format_currency(5_419_843) == "$5.42M"
    assert format_currency(892_842) == "$892.8K"
    assert format_currency(500) == "$500"
