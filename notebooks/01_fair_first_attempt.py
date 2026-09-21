# notebooks/01_fair_first_attempt.py
#
# ─────────────────────────────────────────────────────────────────────────
#  SUPERSEDED — kept as a record of how the FAIR engine was arrived at.
#  Do not import this. The working engine is
#  src/risk_quantification/fair_engine.py.
# ─────────────────────────────────────────────────────────────────────────
#
# This was the first working FAIR model in the project, written while
# learning the methodology. Two things came out of it:
#
#   1. riskquant (Netflix's open-source FAIR library) does not support
#      Python 3.13, so the maths is implemented directly with numpy here.
#      That decision carried through to the production engine.
#
#   2. The annual-loss line below is WRONG, and this file is kept mainly
#      to show where the error was:
#
#          annual_losses = annual_freqs * loss_magnitudes
#
#      That draws ONE loss magnitude per simulated year and multiplies it
#      by the number of events. It forces every event in a year to cost
#      exactly the same amount, which is not what FAIR specifies and which
#      fattens the tail badly — the 99th percentile came out 22-36% too
#      high across the five scenarios.
#
#      FAIR treats each loss event as an independent draw. fair_engine.py
#      sums N independent log-normal draws per year, where N ~ Poisson(λ):
#
#          year_index    = np.repeat(np.arange(n), annual_freqs)
#          annual_losses = np.bincount(year_index, weights=loss_magnitudes)
#
#      The mean ALE barely moved (E[N]·E[X] holds either way). The tail is
#      where the error lived. See notebooks/README.md for the numbers.
#
# The code below is preserved exactly as it was originally written,
# including the unused scipy import.

import numpy as np
from scipy import stats

print("=" * 55)
print("  FAIR Risk Model — Learning the Basics")
print("=" * 55)

def fair_simulation(loss_low, loss_high, freq_low, freq_high, n=100_000):
    """
    Implements FAIR using log-normal distributions.
    This is exactly what riskquant does internally.
    
    loss_low/high  = min/max single loss estimate in dollars
    freq_low/high  = min/max attack attempts per year
    """
    # Log-normal parameters from low/high estimates
    # We treat low as 5th percentile, high as 95th percentile
    log_low  = np.log(loss_low)
    log_high = np.log(loss_high)
    mu       = (log_low + log_high) / 2
    sigma    = (log_high - log_low) / (2 * 1.645)  # 90% confidence interval

    # Simulate individual loss magnitudes
    loss_magnitudes = np.random.lognormal(mean=mu, sigma=sigma, size=n)

    # Simulate annual frequency (Poisson distribution)
    avg_freq        = (freq_low + freq_high) / 2
    annual_freqs    = np.random.poisson(lam=avg_freq, size=n)

    # Annual loss = frequency × magnitude per year
    annual_losses   = annual_freqs * loss_magnitudes
    return annual_losses


# ── Scenario: Ransomware at a fictional Canadian bank ────
losses = fair_simulation(
    loss_low   = 200_000,
    loss_high  = 2_000_000,
    freq_low   = 1,
    freq_high  = 4,
)

print(f"\n  Scenario: Ransomware — First National Bank (Fictional)")
print(f"  Loss range: $200K – $2M per event | Frequency: 1–4x/year")
print(f"\n  Simulation results (100,000 scenarios):")
print(f"  Mean annual loss    : ${np.mean(losses):>12,.0f}")
print(f"  Median annual loss  : ${np.median(losses):>12,.0f}")
print(f"  90th percentile     : ${np.percentile(losses, 90):>12,.0f}")
print(f"  95th percentile     : ${np.percentile(losses, 95):>12,.0f}")
print(f"  99th percentile     : ${np.percentile(losses, 99):>12,.0f}")
print(f"\n  Interpretation:")
print(f"  → Expected annual cost of ransomware: ${np.mean(losses):,.0f}")
print(f"  → 10% chance annual losses exceed:   ${np.percentile(losses, 90):,.0f}")
print("=" * 55)