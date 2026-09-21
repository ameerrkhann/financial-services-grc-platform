# Notebooks — how the FAIR engine got built

Working files kept deliberately, not leftovers. They show the route to
`src/risk_quantification/fair_engine.py`, including a modelling error that
survived several weeks before it was found and fixed.

Nothing in this folder is imported by the platform. It is history.

| File | What it is |
|------|------------|
| `01_fair_first_attempt.py` | The first working FAIR model. Superseded — contains the multiplicative annual-loss bug described below. Runs standalone. |

---

## Step 1 — riskquant would not install

The plan was to use [riskquant](https://github.com/Netflix-Skunkworks/riskquant),
Netflix's open-source FAIR library. It does not support Python 3.13, and no
amount of pinning got it working.

Rather than downgrade the whole project to an older Python, the FAIR maths was
implemented directly with numpy. FAIR is not a complicated model — a Poisson
frequency distribution and a log-normal loss magnitude distribution — so the
dependency was not worth the version ceiling. `riskquant` is deliberately
absent from `requirements.txt`, and `docs/risk_assessment_methodology.md`
explains why.

That turned out to be the right call for a second reason: owning the maths is
what made the next problem findable.

## Step 2 — the annual-loss line was wrong

`01_fair_first_attempt.py` computes a year's loss like this:

```python
loss_magnitudes = np.random.lognormal(mean=mu, sigma=sigma, size=n)
annual_freqs    = np.random.poisson(lam=avg_freq, size=n)
annual_losses   = annual_freqs * loss_magnitudes     # wrong
```

It reads naturally — "loss this year equals number of events times the cost of
an event" — and it produces plausible-looking output, which is why it lasted.
But it draws **one** magnitude per simulated year and multiplies it by the
event count. Every event in a given year therefore costs exactly the same
amount.

FAIR treats each loss event as an **independent** draw. A year with three
ransomware events is three separate draws from the loss distribution, not one
draw counted three times. The multiplicative version understates how often a
bad year is bad because of one severe event and several minor ones, and
overstates the extreme tail, because a single high draw gets multiplied
rather than averaged against its neighbours.

## Step 3 — the fix

`fair_engine.py` draws every event across every year in one vectorised call,
then sums the draws back into the year that produced them:

```python
total_events    = int(annual_freqs.sum())
loss_magnitudes = rng.lognormal(mean=mu, sigma=sigma, size=total_events)
year_index      = np.repeat(np.arange(n), annual_freqs)
annual_losses   = np.bincount(year_index, weights=loss_magnitudes, minlength=n)
```

No Python loop over 100,000 years — `np.repeat` builds the index and
`np.bincount` does the grouped sum.

## What actually changed

Same per-scenario seeds, 100,000 simulated years, old model vs new:

| Scenario | ALE before | ALE after | p99 before | p99 after | p99 change |
|---|---|---|---|---|---|
| Data Breach — Customer PII | $4,967,026 | $4,970,939 | $34,615,820 | $24,002,404 | −30.7% |
| Ransomware Attack | $5,387,155 | $5,419,843 | $39,635,032 | $30,331,715 | −23.5% |
| Insider Threat | $2,008,309 | $2,017,033 | $17,185,386 | $13,342,660 | −22.4% |
| Third-Party Vendor Failure | $2,663,299 | $2,702,990 | $24,230,394 | $20,094,654 | −17.1% |
| Cloud Misconfiguration | $4,403,635 | $4,464,212 | $37,274,063 | $24,008,781 | −35.6% |
| **Portfolio** | **$19.43M** | **$19.58M** | — | — | — |

The mean barely moved, which is exactly what theory predicts: expected annual
loss is `E[N] · E[X]` either way, so both models get the headline ALE right.

The tail is where the error lived, and the tail is the part a bank actually
uses — the 99th percentile is the capital-planning and cyber-insurance number.
The old model would have justified roughly a third more coverage on the data
breach and cloud scenarios than the risk warrants.

## What stops it coming back

`tests/test_fair_engine.py` covers this in two ways:

- **Against closed form.** For every scenario, the simulated ALE must land
  within 3% of the analytic mean `λ · exp(μ + σ²/2)`. The test is pinned to
  theory, not to previously observed output, so it cannot be satisfied by
  whatever the code happens to do today.
- **Against this specific bug.** `test_losses_are_summed_not_multiplied()`
  runs both models on identical inputs and asserts the summed model's
  p99-to-mean ratio is lower. Reintroducing the multiplication fails the test.

## The transferable lesson

The bug did not produce an error, a warning, or an implausible number. It
produced a number that looked right and was wrong in the part of the
distribution nobody eyeballs. That is the normal failure mode of quantitative
risk work.

Two habits catch it, and both are now in the repo: test against a closed-form
result rather than against your own output, and write down the assumption
behind every line that turns inputs into a number. Every assumption in the
model — the Poisson rate being the midpoint of the frequency range, the
low/high pair being a 90% confidence interval, the 60–80% control
effectiveness — is documented in `fair_engine.py` or `scenarios.py` for
exactly that reason.
