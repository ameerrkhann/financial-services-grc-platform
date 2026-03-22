# src/risk_quantification/riskquant_test.py
# FAIR implementation using numpy/scipy directly
# (riskquant incompatible with Python 3.13 — same math, no dependency)

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