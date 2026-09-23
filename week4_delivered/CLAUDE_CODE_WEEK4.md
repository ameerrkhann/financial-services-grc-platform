# Claude Code Brief — Week 4 Integration
## Financial Services Cyber Risk Intelligence Platform

Save this in the repo root, then tell Claude Code:
**"Read CLAUDE_CODE_WEEK4.md and do Phase 1."**

Work through phases in order. **Stop and summarise after each. Ask before any `git push`.**

---

## Context

- **Repo:** `github.com/ameerrkhann/financial-services-grc-platform`
- **Owner:** Ameer Khan — 4th-year CS @ University of Toronto (graduating 2027), Data Analyst I @ Manulife, part-time @ Scotiabank. Targeting GRC roles at Canadian financial institutions.
- **This is a portfolio project.** GRC hiring managers will read it. A wrong control identifier is worse than a missing one — accuracy of framework references matters as much as working code.
- **Platform:** macOS, Python 3.13, virtualenv at `./venv` (`source venv/bin/activate` first).
- **`riskquant` is not used** — it is incompatible with Python 3.13. FAIR is implemented directly with NumPy. Do not try to reinstall it.
- **Database:** SQLite at `src/database/grc_platform.db` (gitignored). Schema `src/database/schema.sql`, access layer `src/database/db_manager.py`.
- **Organisation modelled:** First National Bank (Fictional). All vendor names must be obviously invented.

## What has already been built

A set of corrected, working modules has been delivered in `week4_delivered/`. They are not yet wired into the repo. Your job is to integrate them, not to rewrite them from scratch.

| Delivered file | What it is |
|---|---|
| `fair_engine.py` | Corrected FAIR engine — seeded, validated against the analytic mean within 0.6% |
| `grc_data.py` | Corrected reference data: CSF 2.0 IDs, ISO 27001:2022 controls, OSFI references, 5 scenarios, 8 demo vendors |
| `build_dataset.py` | Generates the full demo dataset and the Power BI export workbook |
| `build_charts.py` | Loss exceedance curves, CSF radar, risk reduction, vendor tiers |
| `build_pdf.py` | 3-page executive summary PDF |
| `build_templates.py` | Excel risk register and control matrix |

Every figure in these outputs is reproducible from seed 42.

## Ground rules

1. Read existing repo code before changing it. Keep the current style — tabulate/colorama terminal output, docstrings, section-comment banners.
2. Small focused commits with clear messages. Show a diff summary per phase.
3. Never commit `grc_platform.db`, `venv/`, `.DS_Store`, or `__pycache__`.
4. **Every number in the README or docs must come from an actual run of the code.**
5. If unsure about a regulatory or framework reference, say so in your phase summary rather than guessing.

---

# Phase 1 — Integrate the corrected engine

### 1a. Replace the FAIR engine

`src/risk_quantification/fair_engine.py` currently computes:

```python
annual_losses = annual_freqs * loss_magnitudes
```

That draws **one** loss magnitude per simulated year and multiplies it by the event count, which assumes every event in a year costs exactly the same and inflates the tail. Replace the file with the delivered `fair_engine.py`, which sums N independent log-normal draws where N ~ Poisson(λ), vectorised via `np.bincount`.

Keep the existing `format_currency` signature so nothing downstream breaks. Report the before/after ALE and p90 per scenario in your summary — the mean should barely move, the tail should shrink.

### 1b. Adopt ROSI in place of the fake ROI

The current "ROI" is `(ALE − control_cost) / ALE`, which is not ROI and implies controls eliminate all risk. The delivered `fair_engine.compute_rosi()` does it properly using a per-scenario `control_effectiveness` assumption.

Update `run_scenarios.py` and `risk_report.py` to use it. Add `control_effectiveness`, `residual_ale` and `rosi_pct` to the `risk_scenarios` table in `schema.sql` and to `db_manager.save_risk_scenario()`.

### 1c. Framework references

Merge the corrected references from the delivered `grc_data.py` into `src/compliance/csf_data.py`, `src/compliance/framework_mapper.py` and `src/risk_quantification/scenarios.py`. Verify each against the primary source before applying.

**NIST CSF 2.0** — these are CSF 1.1 identifiers that no longer exist:

| Currently in repo | Correct CSF 2.0 |
|---|---|
| `PR.AC-01` | `PR.AA-01` (identities and credentials); `PR.AA-03` for authentication/MFA |
| `RS.RP-01` | `RS.MA-01` (incident response plan executed) |
| `RC.IM-01` | `ID.IM-04` (plans maintained and improved — Improvement moved to Identify) |
| `GV.OC-01` used for policy | `GV.PO-01` (GV.OC-01 is organisational mission) |

Correct already: `ID.AM-01`, `ID.RA-01`, `PR.DS-01`, `PR.AT-01`, `DE.CM-01`, `DE.AE-02`, `RS.CO-02`, `RC.RP-01`, `GV.RM-01`.

**ISO/IEC 27001:2022** — the repo says 2022 but uses 2013 numbering:

| In repo (2013) | Correct 2022 |
|---|---|
| `A.9.1` access control | `A.5.15` Access control; `A.8.5` Secure authentication |
| `A.12.4` logging & monitoring | `A.8.15` Logging; `A.8.16` Monitoring activities |
| `A.16.1` incident management | `A.5.24` planning, `A.5.25` assessment, `A.5.26` response, `A.5.27` learning; `A.6.8` event reporting |
| `A.17.1` continuity | `A.5.29` security during disruption; `A.5.30` ICT readiness; backups `A.8.13` |
| `A.8.1` "inventory of assets" | `A.5.9` — in 2022, A.8.1 is *user endpoint devices* |
| `A.5.8` for risk objectives | Clause **6.1** (actions to address risks and opportunities) |

**OSFI** — remove invented section numbers:
- The **24-hour reporting expectation** comes from OSFI's *Technology and Cyber Security Incident Reporting* advisory, not B-13. Cite it as such.
- **B-13 has no data-residency requirement.** Reword the cloud questionnaire reference accordingly.
- **B-13:** in force 1 January 2024. **B-10:** in force 1 May 2024. Verify both.
- **E-21 dates are stale.** Today is September 2026. Full adherence was due **1 September 2026**; scenario testing of all critical operations is due **1 September 2027**. Rewrite every "deadline approaching" line in present tense.

### 1d. Acceptance
Delete the DB, re-run `run_scenarios.py`, `loss_exceedance.py`, `risk_report.py`. All clean. Print old vs new ALE and p90 per scenario.

---

# Phase 2 — Demo data seeder

Wire the delivered `build_dataset.py` into the repo as `src/database/seed_demo_data.py`, adapted to write through `db_manager` rather than straight to JSON/Excel. It must produce:

1. A fresh database.
2. One CSF assessment — Govern 2, Identify 2, Protect 3, Detect 2, Respond 1, Recover 3, with rationales and a target score of 4 per function. Add `target_score` to `function_scores` (or a `csf_targets` table). Reuse `scoring_engine.py`'s gap generation rather than duplicating it.
3. All 5 FAIR scenarios at seed 42.
4. The 8 fictional vendors, scored through `vendor_risk.scoring.calculate_score` so results match the Streamlit app. Three must be past their reassessment window so `get_overdue_vendors()` returns rows.

Then fold the delivered export logic into `src/reporting/export_for_powerbi.py`.

**Critical constraint:** the existing Power BI report refreshes from this workbook. Power Query fails on a **removed** column but tolerates added ones. Keep every column the current export produces — including the placeholder `note` column on the `ControlGaps` sheet — and keep all `<Sheet>_tbl` table names unchanged. Adding columns and new sheets is fine.

**Acceptance:** `python3 src/database/seed_demo_data.py && python3 src/reporting/export_for_powerbi.py` runs clean and every sheet has rows.

---

# Phase 3 — Wire in the generators

Place the delivered generators in the repo and confirm each runs end to end:

- `build_charts.py` → `src/reporting/build_charts.py`, writing to `dashboards/`
- `build_pdf.py` → `src/reporting/executive_summary.py`, writing `docs/executive_summary.pdf`
- `build_templates.py` → `src/reporting/build_templates.py`, writing to `templates/`

Add `reportlab` to `requirements.txt`. The chart palette is deliberately chosen: the five series colours pass colourblind-safety checks (worst adjacent CVD ΔE 8.4 on the dark surface). **Do not substitute different colours** — the previous cyan/red/green/orange palette failed, with green and orange at ΔE 5.5 for deuteranopia.

---

# Phase 4 — Tests

Add `pytest` to requirements and create `tests/`:

- **`test_fair_engine.py`** — with a fixed seed, ALE within 3% of the analytic mean `λ · exp(μ + σ²/2)`; percentiles ordered (median ≤ p90 ≤ p95 ≤ p99); zero-frequency edge case returns zeros.
- **`test_vendor_scoring.py`** — all-Yes = 100/Low; all-No = 0/Critical; N/A excluded from the denominator; tier boundaries at 40/41, 60/61, 80/81.
- **`test_gap_analysis.py`** — only scores below 3 produce gaps; ordering by risk score is correct.
- **`test_db_manager.py`** — round-trip insert/read against a temporary DB.

`DB_PATH` in `db_manager.py` is hard-coded — add a `GRC_DB_PATH` environment override so tests never touch the real database.

Add `.github/workflows/tests.yml` running pytest on push (Python 3.13, ubuntu-latest). Tests must pass locally before committing.

---

# Phase 5 — README and docs

Rewrite `README.md` as the final "project complete" version.

1. Title, one-line pitch, status **✅ Complete**.
2. ⚠️ The byline reads "3rd Year CS @ University of Toronto" — change it to **4th Year** everywhere it appears (README, docs, any script header).
3. Badges: Python 3.13, tests (GitHub Actions), MIT licence.
4. **Hero image row** — these files will be in `dashboards/`: `lec_all_scenarios.png`, `csf_radar.png`, `risk_reduction.png`, `vendor_tiers.png`, plus `powerbi_risk_overview.png`, `powerbi_csf_maturity.png`, `powerbi_vendor_risk.png` and `streamlit_vendor_app.png` which Ameer will add.
5. **Architecture diagram** as a **Mermaid** block — GitHub renders these natively. Three modules → SQLite → export → Power BI / PDF / Excel.
6. Module sections — keep the good prose, but **regenerate every table of numbers from current code output**.

   ⚠️ The live README claims ALEs of ~$2.1M/$2.8M and a ~$9.4M portfolio total. The actual figures are:

   | Scenario | ALE | 90th percentile | Control cost | Residual ALE | ROSI |
   |---|---|---|---|---|---|
   | Ransomware | $5.45M | $14.05M | $500K | $1.36M | 717% |
   | Data Breach | $4.99M | $11.86M | $350K | $1.50M | 898% |
   | Cloud Misconfiguration | $4.46M | $10.30M | $180K | $892K | 1,883% |
   | Vendor Failure | $2.68M | $7.53M | $200K | $937K | 770% |
   | Insider Threat | $2.03M | $5.31M | $280K | $814K | 336% |
   | **Total** | **$19.61M** | — | **$1.51M** | **$5.50M** | — |

   Fix this in the README **and** `docs/risk_assessment_methodology.md`.
7. **Deliverables table** — Power BI report (`dashboards/GRC_Risk_Dashboard.pbix`), `docs/executive_summary.pdf`, `templates/risk_register.xlsx`, `templates/control_matrix.xlsx`.
8. **How to run** — fix the clone URL to `ameerrkhann` (currently `YOUR_USERNAME`), add `seed_demo_data.py` as step one, plus pytest, the export script, and the PDF and template builders.
9. **Methodology and limitations** — state plainly that loss ranges are interpreted as the 5th/95th percentile of a log-normal, so the mean sits above the midpoint of the stated range; that scenarios are modelled independently; that control effectiveness is assumed, not measured; and that control costs cover incremental tooling only, excluding staffing, which makes ROSI an upper bound.
10. Regulatory framework table with corrected dates and references.
11. Interview-prep table — keep it, update the E-21 wording.
12. **Remove the "Coming in Week 4" section.**

Also:
- Update all `docs/` files for the Phase 1 reference corrections and the new figures.
- `src/risk_quantification/riskquant_test.py` is a throwaway learning file — **ask** whether to delete it or move it to `notebooks/`.
- Add `docs/week4_deliverables.md` listing each deliverable and how it was produced.
- **Final check:** every image and file linked in the README exists in the repo; `pip install -r requirements.txt` works in a fresh venv; `pytest` passes.

---

# Phase 6 — Commit and push

Show `git status` and the commit list. **Wait for approval, then push to `main`.**
