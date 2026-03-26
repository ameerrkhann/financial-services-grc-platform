### Methodology: FAIR (Factor Analysis of Information Risk)
FAIR implemented from scratch using numpy and scipy log-normal 
and Poisson distributions — the same statistical approach used 
internally by Netflix's riskquant library.

### Scenario Parameters Summary

| Scenario | Loss Range | Frequency/Year | Control Cost |
|----------|-----------|----------------|--------------|
| Data Breach | $500K – $8M | 0.5 – 3.0x | $350K |
| Ransomware | $800K – $12M | 0.5 – 2.0x | $500K |
| Insider Threat | $200K – $5M | 0.5 – 2.0x | $280K |
| Vendor Failure | $400K – $9M | 0.3 – 1.5x | $200K |
| Cloud Misconfiguration | $150K – $6M | 1.0 – 4.0x | $180K |

### Parameter Rationale
Loss ranges are calibrated to Canadian financial services context using 
publicly reported breach costs from OSFI incident disclosures, IBM Cost 
of a Data Breach Report (Canada), and Ponemon Institute financial sector 
benchmarks. Frequency estimates reflect the threat landscape for a 
mid-size federally regulated financial institution.