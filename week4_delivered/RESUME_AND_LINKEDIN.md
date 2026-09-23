# Resume, LinkedIn and Launch Content
**Ameer Mohammad Khan** — every figure below comes from an actual run of the platform.

---

## Reference figures

| Figure | Value |
|---|---|
| Portfolio annualised loss expectancy | $19.61M |
| Residual ALE after controls | $5.50M |
| Annual control investment modelled | $1.51M |
| Risk reduction | $14.11M |
| Largest single exposure | Ransomware — $5.45M ALE, $14.05M at the 90th percentile |
| NIST CSF 2.0 overall maturity | 2.2 / 5.0 (target 4.0) |
| Open control gaps | 4 |
| Controls cross-mapped | 16 across NIST CSF 2.0, ISO 27001:2022, SOC 2, OSFI |
| Vendors assessed | 8 (1 Critical, 2 High, 3 Medium, 2 Low) |
| Vendors overdue for reassessment | 3 |
| Simulations per scenario | 100,000 |

---

# 1. Resume — Projects section

Place under **Projects**. If you only have space for one project, this is it.

> **Financial Services Cyber Risk Intelligence Platform** — *Personal Project, 2026*
> *Python · SQL/SQLite · Power BI · Streamlit · NumPy/SciPy · Matplotlib*
>
> - Built a three-module GRC platform modelling a cyber risk programme for a simulated Canadian financial institution, aligned to NIST CSF 2.0, ISO 27001:2022, SOC 2 and OSFI B-10, B-13 and E-21.
> - Implemented FAIR risk quantification from scratch using Poisson frequency and log-normal severity distributions across 100,000 Monte Carlo simulations per scenario, quantifying **$19.6M** in annualised loss expectancy across five threat scenarios and identifying **$14.1M** of risk reduction available for **$1.5M** in annual control investment.
> - Developed a NIST CSF 2.0 maturity scoring engine producing gap analysis and an effort-ranked 90-day remediation roadmap, with automated control mapping across three frameworks so one control satisfies NIST, ISO 27001 and SOC 2 simultaneously.
> - Built an OSFI B-10 aligned third-party risk assessor in Streamlit: service-type-specific questionnaires, weighted scoring, automated Critical/High/Medium/Low tiering, and a SQLite audit trail that flags vendors past their reassessment window.
> - Delivered a three-page Power BI report, a board-ready executive summary PDF, and Excel risk register and control matrix templates with inherent/residual risk calculations.

### Shorter version (if space is tight)

> **Financial Services Cyber Risk Intelligence Platform** — *Personal Project, 2026*
> *Python · SQL · Power BI · Streamlit*
>
> - Built a GRC platform quantifying **$19.6M** in annualised cyber loss across five threat scenarios using FAIR and Monte Carlo simulation, aligned to NIST CSF 2.0 and OSFI B-10/B-13/E-21.
> - Developed a NIST CSF 2.0 maturity scorer with cross-framework mapping to ISO 27001:2022 and SOC 2, and an OSFI B-10 vendor risk assessor with automated risk tiering and audit trail.
> - Delivered Power BI dashboards, a board-ready executive summary, and Excel risk register templates.

### Skills line

> **Frameworks:** NIST CSF 2.0 · ISO 27001:2022 · SOC 2 · FAIR · OSFI B-10, B-13, E-21
> **Technical:** Python (pandas, NumPy, SciPy) · SQL/SQLite · Power BI · Streamlit · Git
> **Certification:** ISC2 Certified in Cybersecurity (in progress)

---

# 2. LinkedIn profile

### Headline
> Cybersecurity GRC | NIST CSF 2.0 · FAIR · OSFI B-10/B-13 | Data Analyst @ Manulife | 4th Year CS @ University of Toronto

### About

> I work with data at Manulife and Scotiabank — two federally regulated institutions where cyber risk is a board-level concern, not an IT footnote. That's where my interest in GRC started.
>
> Over the past month I built a cyber risk intelligence platform for a simulated Canadian bank. Three modules: a NIST CSF 2.0 maturity scorer with cross-framework mapping to ISO 27001 and SOC 2, a FAIR risk quantification engine running Monte Carlo simulations to express cyber risk in dollars, and an OSFI B-10 aligned third-party risk assessor.
>
> The thing I keep coming back to is the translation problem. A board can't budget against "ransomware is high risk." It can budget against "$5.4M expected annual loss, with a one-in-ten-year loss of $14M, against $500K in controls." Getting from one to the other is the work.
>
> I'm finishing my CS degree at the University of Toronto (2027) and working toward the ISC2 CC certification. Looking for GRC and cyber risk roles in Canadian financial services.

### Featured section
Add the GitHub repo and pin the launch post.

---

# 3. LinkedIn launch post

Combined Week 3 + 4 post. **Rewrite this in your own voice** — the structure matters more than the words.

---

Most cybersecurity resumes list "NIST CSF" as a skill. I wanted to find out what it actually takes to operate one.

So I spent 30 days building a cyber risk platform for a simulated Canadian bank. Three modules:

**1. NIST CSF 2.0 maturity scoring** — scores all six functions, generates a gap analysis, and maps every control to its ISO 27001:2022 and SOC 2 equivalent. One control, three frameworks, no duplicate audit work.

**2. FAIR risk quantification** — this is the one that changed how I think. It runs 100,000 Monte Carlo simulations per threat scenario and converts cyber risk into dollars. The bank carries $19.6M in expected annual loss across five scenarios. Ransomware alone is $5.4M, with a one-in-ten-year loss of $14M.

**3. OSFI B-10 vendor risk assessment** — a Streamlit app that generates questionnaires by vendor type, scores responses, assigns risk tiers, and keeps the audit trail OSFI expects. Of eight vendors assessed, three were past their reassessment window.

**Three things I didn't expect:**

Cloud misconfiguration had the *lowest* cost per incident but the *highest* frequency — which made it a bigger annual exposure than scenarios that sound far scarier. Frequency is half the equation and it's the half people skip.

Govern is the function organisations score lowest on, and it was only added to CSF in 2024. Without it, the other five don't hold. It was also the cheapest gap to close in my model — roughly four weeks of work.

And the one that stung: my first implementation had a subtle bug in the Monte Carlo loop. It reused a single loss magnitude per simulated year instead of drawing each event independently, which inflated the tail. Finding that mattered more than any feature I shipped.

**Why Canadian financial services specifically:** I work at Manulife and part-time at Scotiabank. Both are OSFI-regulated. E-21 full adherence was due September 1st this year, and scenario testing across all critical operations is due September 2027 — so this isn't abstract. It's what these institutions are actively building.

Everything's on GitHub — code, executive summary, dashboards, methodology.

I'm looking for GRC and cyber risk roles in Canadian financial services. If you're hiring or know someone who is, I'd welcome the conversation.

\#GRC #Cybersecurity #NISTCSF #FAIR #OSFI #RiskManagement #Python #CanadianFinance

---

### Images to attach (in this order)
1. `lec_all_scenarios.png` — the loss exceedance curves, your strongest visual
2. Power BI Risk Overview page screenshot
3. `csf_radar.png` — the maturity radar
4. Streamlit vendor assessor screenshot

### Posting notes
- Tuesday–Thursday, 8–10am ET
- Put the GitHub link in the **first comment**, not the post body — LinkedIn suppresses reach on posts with external links
- Reply to every comment in the first two hours

---

# 4. Cover letter opening

> I'm a fourth-year Computer Science student at the University of Toronto, graduating in 2027, currently working as a Data Analyst at Manulife and part-time at Scotiabank. Over the past month I built a cyber risk intelligence platform aligned to NIST CSF 2.0, FAIR and OSFI B-10/B-13 — quantifying $19.6M in annualised loss exposure for a simulated Canadian bank and producing the board-level reporting that goes with it. I'd like to bring that same applied approach to [company].

---

# 5. Where to apply

**Start internal.** You already work at Manulife and Scotiabank. Internal moves are far easier than external applications, and you now have something concrete to point at. Check both internal job boards this week, and message someone on the security or risk team — that message writes itself now.

**External:** RBC, TD, BMO, CIBC, Sun Life, Interac, Payments Canada, Canada Life, EQ Bank, Wealthsimple, and OSFI itself.

**Search terms:** GRC Analyst · Cyber Risk Analyst · Third Party Risk Analyst · IT Risk Analyst · Security Compliance Analyst · Operational Resilience Analyst · Technology Risk Analyst

**Cadence:** 5 applications this week, then 3–5 per week. Tailor the top bullet to each posting's language — if it says "third-party risk management," make that phrase appear in your resume.

---

# 6. Interview prep

| Question | Where your answer comes from |
|---|---|
| Walk me through NIST CSF 2.0 | Six functions. Govern was added in 2024 and sits above the rest. |
| How do you quantify cyber risk? | FAIR: Poisson frequency × log-normal severity, 100,000 simulations, output is ALE and a loss exceedance curve. |
| Why FAIR over High/Medium/Low? | A board can't budget against "high." $5.4M vs $500K in controls is a decision. |
| What's a loss exceedance curve? | Read it at any dollar figure to get the probability annual losses exceed it. |
| How do you assess a vendor? | Tier by risk, questionnaire weighted by control importance, score, assign tier, monitor, keep the audit trail. |
| What is OSFI B-10? B-13? E-21? | B-10 third-party risk (in force May 2024). B-13 technology and cyber risk (January 2024). E-21 operational resilience — full adherence September 2026, scenario testing September 2027. |
| RTO vs impact tolerance? | RTO is what the institution can achieve. Impact tolerance is how long customers can bear the disruption. E-21 works from the second. |
| Tell me about a project you're proud of | Lead with the problem it solves, not the libraries. And mention the Monte Carlo bug — finding your own mistakes reads as maturity. |

**The one habit:** when asked about the project, open with what it does for a decision-maker. "It turns cyber risk into dollar figures a board can budget against" lands better than "it uses NumPy and SciPy."
