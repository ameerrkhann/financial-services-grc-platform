# src/risk_quantification/fair_engine.py
# Core FAIR simulation engine
# Implements log-normal loss magnitude + Poisson event frequency

import numpy as np

N_SIMULATIONS = 100_000  # number of Monte Carlo runs
BASE_SEED     = 42       # anchor for reproducible runs across every module


def seed_for(scenario_id, base=BASE_SEED):
    """
    Returns a deterministic per-scenario seed.

    Every module that simulates a scenario (run_scenarios, loss_exceedance,
    the Power BI export, the executive PDF) uses this so the ALE printed in
    one place matches the ALE printed everywhere else.
    """
    return base * 1_000 + int(scenario_id)


def run_fair_simulation(loss_low, loss_high, freq_low, freq_high,
                        n=N_SIMULATIONS, seed=None):
    """
    Runs a FAIR Monte Carlo simulation.

    Each simulated year draws an event count N ~ Poisson(lambda), then draws
    N *independent* log-normal loss magnitudes and sums them. Summing per-event
    draws is what FAIR specifies — multiplying one magnitude by the event count
    would make every event in a year cost exactly the same, which inflates the
    tail percentiles.

    Assumption: lambda is the mean of freq_low and freq_high. The low/high pair
    is treated as a plausible range for the annual event rate rather than as
    distribution percentiles, so its midpoint becomes the Poisson mean.

    Loss magnitude assumption: loss_low is the 5th percentile and loss_high the
    95th percentile of a log-normal distribution (a 90% confidence interval).

    Parameters
    ----------
    loss_low  : float  — minimum single-event loss estimate ($)
    loss_high : float  — maximum single-event loss estimate ($)
    freq_low  : float  — minimum loss events per year
    freq_high : float  — maximum loss events per year
    n         : int    — number of simulated years
    seed      : int    — optional seed for a reproducible run

    Returns
    -------
    dict with simulation results
    """
    rng = np.random.default_rng(seed)

    # Log-normal parameters
    # Treat low as 5th percentile, high as 95th percentile (90% CI)
    log_low  = np.log(loss_low)
    log_high = np.log(loss_high)
    mu       = (log_low + log_high) / 2
    sigma    = (log_high - log_low) / (2 * 1.645)

    # Event count per simulated year
    avg_freq     = (freq_low + freq_high) / 2
    annual_freqs = rng.poisson(lam=avg_freq, size=n)

    # One independent magnitude per event across all years, drawn in a single
    # vectorised call, then summed back into the year that produced it.
    total_events    = int(annual_freqs.sum())
    loss_magnitudes = rng.lognormal(mean=mu, sigma=sigma, size=total_events)
    year_index      = np.repeat(np.arange(n), annual_freqs)
    annual_losses   = np.bincount(year_index, weights=loss_magnitudes, minlength=n)

    return {
        "annual_losses":  annual_losses,
        "ale":            float(np.mean(annual_losses)),
        "median":         float(np.median(annual_losses)),
        "percentile_90":  float(np.percentile(annual_losses, 90)),
        "percentile_95":  float(np.percentile(annual_losses, 95)),
        "percentile_99":  float(np.percentile(annual_losses, 99)),
        "prob_over_1m":   float(np.mean(annual_losses > 1_000_000) * 100),
        "prob_over_5m":   float(np.mean(annual_losses > 5_000_000) * 100),
        "mean_events":    float(np.mean(annual_freqs)),
    }


def compute_rosi(ale, control_cost, control_effectiveness):
    """
    Return on Security Investment for a control set.

        residual_ale   = ale * (1 - control_effectiveness)
        risk_reduction = ale - residual_ale
        rosi           = (risk_reduction - control_cost) / control_cost

    ROSI is expressed as a ratio (0.5 = 50% return). control_effectiveness is
    an *assumption* about how much of the annual expected loss the control set
    removes — it is documented per scenario in scenarios.py, not measured.

    Returns a dict so callers can store or print any part of the calculation.
    """
    residual_ale   = ale * (1 - control_effectiveness)
    risk_reduction = ale - residual_ale
    rosi           = ((risk_reduction - control_cost) / control_cost
                      if control_cost else 0.0)

    return {
        "residual_ale":   residual_ale,
        "risk_reduction": risk_reduction,
        "rosi":           rosi,
        "rosi_pct":       rosi * 100,
    }


def format_currency(value):
    """Formats a number as a clean dollar string."""
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:.0f}"
