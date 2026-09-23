# Week 4 — What's Done and What's Left

The heavy lifting is finished. Everything in `week4_delivered/` was built and verified: the corrected dataset, four charts, the executive PDF, both Excel templates, and a three-page Power BI file.

What remains is the part that needs you: loading the data into Power BI, taking screenshots, letting Claude Code integrate the code into your repo, and applying.

---

## Contents of the delivery

```
week4_delivered/
├── GRC_Risk_Dashboard.pbix        3-page Power BI report
├── grc_powerbi_data.xlsx          corrected dataset, 9 sheets
├── executive_summary.pdf          3-page CISO briefing
├── templates/
│   ├── risk_register.xlsx         20 columns, live formulas, dropdowns
│   └── control_matrix.xlsx        16 controls, cross-framework, summary sheet
├── charts/
│   ├── lec_all_scenarios.png      loss exceedance curves
│   ├── csf_radar.png              maturity radar, current vs target
│   ├── risk_reduction.png         residual vs reduced risk
│   └── vendor_tiers.png           vendor portfolio by tier
├── src/                           the generator scripts, for the repo
├── CLAUDE_CODE_WEEK4.md           integration brief
├── RESUME_AND_LINKEDIN.md         resume bullets, profile copy, launch post
└── WEEK4_PLAN.md                  this file
```

---

## Day 23 — Power BI (45 minutes)

**Order matters here.** The data must be refreshed before the new pages will populate, because the two new pages reference columns that do not exist in your current model yet.

### Step 1 — Replace the data
1. Open OneDrive and upload `grc_powerbi_data.xlsx`, replacing the old file of the same name
2. In Power BI, open your dataset and choose **Refresh now**
3. Wait for it to finish

The export deliberately keeps every column your current queries expect, including the placeholder `note` column on the ControlGaps sheet, so the refresh will not break.

### Step 2 — Load the report
1. **My workspace → Upload → Browse** → select `GRC_Risk_Dashboard.pbix`
2. Open it. You should see three page tabs: **Risk Overview**, **CSF Maturity**, **Vendor Risk**

### Step 3 — Check and screenshot
Click through all three pages. Screenshot each one:
- `powerbi_risk_overview.png`
- `powerbi_csf_maturity.png`
- `powerbi_vendor_risk.png`

**If a visual shows an error**, the refresh did not complete or a column is missing. Re-run step 1. If it persists, tell me which visual and which page — the fix is usually one field.

### Step 4 — Streamlit screenshot
```bash
source venv/bin/activate
streamlit run src/vendor_risk/app.py
```
Run one assessment through to the gap report and screenshot it as `streamlit_vendor_app.png`.

Put all four screenshots in `dashboards/` in your repo.

---

## Day 24 — Claude Code integration (1 hour)

Copy `week4_delivered/` into your repo, then in Claude Code:

> Read CLAUDE_CODE_WEEK4.md and do Phase 1.

Phase 1 fixes real problems: the Monte Carlo bug, the ROI formula, and framework references that were citing NIST CSF 1.1 and ISO 27001:2013 while claiming 2.0 and 2022. Review its summary, then work through Phases 2 to 6.

Ask it to stop before pushing so you can look at the diff.

---

## Day 25 — Review the documents (45 minutes)

**Executive summary PDF** — read it as if a CISO handed it to you:
- [ ] Does the opening paragraph make sense to someone with no security background?
- [ ] Do the figures match your Power BI pages?
- [ ] Is the "simulated organisation" disclaimer clearly visible?
- [ ] Would you be comfortable emailing this to a manager?

**Excel templates** — open both:
- [ ] Type a likelihood and impact into a blank row of the risk register — does Inherent Risk calculate and the rating colour itself?
- [ ] Do the Treatment and Status dropdowns work?
- [ ] Does the control matrix Summary sheet count correctly when you change a Test Result?

If anything reads awkwardly, say so and I'll fix it. This PDF is your strongest interview artifact — print a copy to bring with you.

---

## Day 26 — Repo polish (45 minutes)

After Claude Code finishes Phase 5:

1. **Read the README on GitHub**, not locally — does it hold your attention for 30 seconds?
2. **Check every image renders** in the browser
3. **Add a licence** — repo → Add file → Create new file → name it `LICENSE` → GitHub offers templates → pick **MIT**
4. **Add topics** — gear icon next to "About": `cybersecurity`, `grc`, `nist-csf`, `risk-management`, `fair`, `osfi`, `python`, `streamlit`, `power-bi`
5. **Set the About description:** *"Python GRC platform: NIST CSF 2.0 maturity scoring, FAIR risk quantification, and OSFI B-10 vendor risk assessment for Canadian financial services."*

---

## Day 27 — Resume and LinkedIn profile (1 hour)

Everything you need is in `RESUME_AND_LINKEDIN.md` — resume bullets with real figures, headline, About section, and the skills line.

One thing to watch: scan your existing resume and LinkedIn for stale **"3rd year"** wording before you start applying.

---

## Day 28 — Launch post and applications (1.5 hours)

The post draft is in `RESUME_AND_LINKEDIN.md`. Rewrite it in your own voice — the structure matters more than the words.

- Attach the four images listed there
- Put the GitHub link in the **first comment**, not the post body
- Post Tuesday to Thursday, 8–10am ET

Then apply to five roles. Start with the internal boards at Manulife and Scotiabank — you work there, and internal moves are far easier than cold applications. You now have something concrete to point at, which makes that outreach message write itself.

---

## After Day 28

- 3–5 applications per week, consistently
- Finish the ISC2 CC — it pairs directly with this project
- Add to the platform when you learn something; a repo with recent commits looks alive
- Message one person a week in Canadian financial services GRC

---

## Notes on what was built

**The FAIR engine had a bug.** The original line `annual_losses = annual_freqs * loss_magnitudes` drew one loss magnitude per simulated year and multiplied it by the event count — which assumes every incident in a year costs identically. The corrected version sums independent draws. Mean ALE barely moved; the tail percentiles came down. This is worth mentioning in interviews.

**The chart palette was changed for a reason.** The original cyan/red/yellow/orange/green set failed colourblind-safety validation — green and orange sat at ΔE 5.5 for deuteranopia, which affects roughly 8% of men. The new palette passes at ΔE 8.4 worst-case. Don't swap the colours back.

**Control costs are tooling-only.** They exclude staffing, which is why the ROSI percentages look high. That limitation is stated in the PDF and should stay in the README.
