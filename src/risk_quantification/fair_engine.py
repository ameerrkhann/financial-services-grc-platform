# src/risk_quantification/fair_engine.py
# Core FAIR simulation engine
# Implements log-normal loss magnitude + Poisson frequency

import numpy as np

N_SIMULATIONS = 100_000  # number of Monte Carlo runs


def run_fair_simulation(loss_low, loss_high, freq_low, freq_high, n=N_SIMULATIONS):
    """
    Runs a FAIR Monte Carlo simulation.

    Parameters
    ----------
    loss_low  : float  — minimum single-event loss estimate ($)
    loss_high : float  — maximum single-event loss estimate ($)
    freq_low  : float  — minimum attack attempts per year
    freq_high : float  — maximum attack attempts per year
    n         : int    — number of simulations

    Returns
    -------
    dict with simulation results
    """
    # Log-normal parameters
    # Treat low as 5th percentile, high as 95th percentile (90% CI)
    log_low  = np.log(loss_low)
    log_high = np.log(loss_high)
    mu       = (log_low + log_high) / 2
    sigma    = (log_high - log_low) / (2 * 1.645)

    # Simulate loss magnitudes and annual frequencies
    loss_magnitudes = np.random.lognormal(mean=mu, sigma=sigma, size=n)
    avg_freq        = (freq_low + freq_high) / 2
    annual_freqs    = np.random.poisson(lam=avg_freq, size=n)

    # Annual loss per scenario
    annual_losses   = annual_freqs * loss_magnitudes

    return {
        "annual_losses":  annual_losses,
        "ale":            float(np.mean(annual_losses)),
        "median":         float(np.median(annual_losses)),
        "percentile_90":  float(np.percentile(annual_losses, 90)),
        "percentile_95":  float(np.percentile(annual_losses, 95)),
        "percentile_99":  float(np.percentile(annual_losses, 99)),
        "prob_over_1m":   float(np.mean(annual_losses > 1_000_000) * 100),
        "prob_over_5m":   float(np.mean(annual_losses > 5_000_000) * 100),
    }


def format_currency(value):
    """Formats a number as a clean dollar string."""
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:.0f}"