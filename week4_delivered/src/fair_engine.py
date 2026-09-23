# fair_engine.py
# FAIR Monte Carlo simulation engine.
#
# Implements the Factor Analysis of Information Risk model directly with numpy.
# (The Netflix `riskquant` package is not compatible with Python 3.13, so the
# same statistical approach — log-normal magnitude, Poisson frequency — is
# implemented here.)
#
# Model
# -----
#   Loss magnitude  X ~ LogNormal(mu, sigma)
#       mu    = (ln(loss_low) + ln(loss_high)) / 2
#       sigma = (ln(loss_high) - ln(loss_low)) / (2 * 1.645)
#       i.e. loss_low and loss_high are treated as the 5th and 95th
#       percentiles of the single-event loss distribution.
#
#   Annual event count  N ~ Poisson(lambda)
#       lambda = mean of (freq_low, freq_high)
#
#   Annual loss for one simulated year = sum of N INDEPENDENT draws of X.
#
# The independence of each event draw matters: multiplying one magnitude by
# the event count (a common shortcut) overstates the tail, because it assumes
# every event in a year costs exactly the same.

import numpy as np

Z_90 = 1.645  # z-score bounding a 90% central interval


def lognormal_params(loss_low, loss_high):
    """Returns (mu, sigma) for a log-normal fitted to a 5th/95th percentile range."""
    if loss_low <= 0 or loss_high <= loss_low:
        raise ValueError("loss_high must exceed loss_low, and both must be positive")
    log_low = np.log(loss_low)
    log_high = np.log(loss_high)
    mu = (log_low + log_high) / 2.0
    sigma = (log_high - log_low) / (2.0 * Z_90)
    return mu, sigma


def analytic_ale(loss_low, loss_high, freq_low, freq_high):
    """Closed-form expected annual loss: lambda * E[X]. Used to validate the simulation."""
    mu, sigma = lognormal_params(loss_low, loss_high)
    lam = (freq_low + freq_high) / 2.0
    return lam * float(np.exp(mu + sigma**2 / 2.0))


def run_fair_simulation(loss_low, loss_high, freq_low, freq_high,
                        n=100_000, seed=None):
    """
    Runs a FAIR Monte Carlo simulation.

    Each simulated year draws an event count from a Poisson distribution and
    then sums that many independent log-normal loss draws.

    Returns a dict of the loss distribution and its summary statistics.
    """
    rng = np.random.default_rng(seed)
    mu, sigma = lognormal_params(loss_low, loss_high)
    lam = (freq_low + freq_high) / 2.0

    # Event count per simulated year
    counts = rng.poisson(lam=lam, size=n)
    total_events = int(counts.sum())

    # One independent magnitude draw per event, summed back per year.
    # np.bincount over a year-index repeated by event count does this in
    # a single vectorised pass — no Python loop over 100,000 years.
    annual_losses = np.zeros(n, dtype=float)
    if total_events > 0:
        magnitudes = rng.lognormal(mean=mu, sigma=sigma, size=total_events)
        year_index = np.repeat(np.arange(n), counts)
        annual_losses = np.bincount(year_index, weights=magnitudes, minlength=n)

    return {
        "annual_losses": annual_losses,
        "ale": float(np.mean(annual_losses)),
        "median": float(np.median(annual_losses)),
        "percentile_90": float(np.percentile(annual_losses, 90)),
        "percentile_95": float(np.percentile(annual_losses, 95)),
        "percentile_99": float(np.percentile(annual_losses, 99)),
        "prob_over_1m": float(np.mean(annual_losses > 1_000_000) * 100),
        "prob_over_5m": float(np.mean(annual_losses > 5_000_000) * 100),
        "prob_zero_loss": float(np.mean(annual_losses == 0) * 100),
        "lambda": lam,
        "mu": float(mu),
        "sigma": float(sigma),
    }


def compute_rosi(ale, control_cost, control_effectiveness):
    """
    Return on Security Investment.

        residual_ale   = ale * (1 - effectiveness)
        risk_reduction = ale - residual_ale
        rosi           = (risk_reduction - control_cost) / control_cost

    control_effectiveness is an assumption, not a measured value.
    """
    residual_ale = ale * (1.0 - control_effectiveness)
    risk_reduction = ale - residual_ale
    rosi = ((risk_reduction - control_cost) / control_cost) if control_cost else 0.0
    return {
        "residual_ale": residual_ale,
        "risk_reduction": risk_reduction,
        "rosi": rosi,
        "rosi_pct": rosi * 100.0,
    }


def format_currency(value):
    """Formats a number as a compact dollar string."""
    if value is None:
        return "—"
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value/1_000:.0f}K"
    return f"${value:,.0f}"
