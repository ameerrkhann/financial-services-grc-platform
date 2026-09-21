# src/reporting/export_for_powerbi.py
# Exports all GRC data from SQLite into one Excel file for Power BI.
# One file → multiple sheets, one per dashboard data source.

import sys
import os
import numpy as np
import pandas as pd
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.database.db_manager import get_connection, initialise_database
from src.risk_quantification.fair_engine import run_fair_simulation, seed_for
from src.risk_quantification.scenarios import SCENARIOS

OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), "../../dashboards")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "grc_powerbi_data.xlsx")


def band_likelihood(avg_freq):
    if avg_freq < 1.0:
        return "Low"
    elif avg_freq <= 2.0:
        return "Medium"
    return "High"


def band_impact(loss_high):
    if loss_high < 5_000_000:
        return "Medium"
    elif loss_high < 9_000_000:
        return "High"
    return "Critical"


def get_risk_scenarios_df(conn):
    rows = conn.execute("""
        SELECT scenario_name, loss_low, loss_high, freq_low, freq_high,
               ale, median, percentile_90, percentile_95,
               prob_over_1m, prob_over_5m, control_cost
        FROM risk_scenarios
        WHERE id IN (SELECT MAX(id) FROM risk_scenarios GROUP BY scenario_key)
    """).fetchall()
    df = pd.DataFrame([dict(r) for r in rows])
    if not df.empty:
        df["avg_frequency"]   = (df["freq_low"] + df["freq_high"]) / 2
        df["likelihood_band"] = df["avg_frequency"].apply(band_likelihood)
        df["impact_band"]     = df["loss_high"].apply(band_impact)
        for col in ["ale", "median", "percentile_90", "percentile_95"]:
            df[col] = df[col].round(0)
    return df


def get_lec_df():
    """
    Recomputes loss exceedance curve points for each scenario.

    Uses the same per-scenario seeds as run_scenarios.py so the curve in Power
    BI is drawn from the identical simulation that produced the stored ALE.
    """
    records = []
    for key, scenario in SCENARIOS.items():
        result   = run_fair_simulation(
            loss_low  = scenario["loss_low"],
            loss_high = scenario["loss_high"],
            freq_low  = scenario["freq_low"],
            freq_high = scenario["freq_high"],
            seed      = seed_for(scenario["id"]),
        )
        losses   = result["annual_losses"]
        max_loss = np.percentile(losses, 99.5)
        for lp in np.linspace(0, max_loss, 100):
            records.append({
                "scenario_name":  scenario["name"],
                "loss_value":     round(float(lp), 0),
                "exceedance_pct": round(float(np.mean(losses > lp) * 100), 2),
            })
    return pd.DataFrame(records)


def get_table_df(conn, query):
    rows = conn.execute(query).fetchall()
    return pd.DataFrame([dict(r) for r in rows])


def main():
    initialise_database()
    conn = get_connection()
    print("Exporting data for Power BI...\n")

    sheets = {}

    sheets["RiskScenarios"] = get_risk_scenarios_df(conn)
    print(f"  RiskScenarios     : {len(sheets['RiskScenarios'])} rows")

    sheets["LossExceedance"] = get_lec_df()
    print(f"  LossExceedance    : {len(sheets['LossExceedance'])} rows")

    sheets["CSFScores"] = get_table_df(conn, """
        SELECT function_name, score, rationale
        FROM function_scores
        WHERE assessment_id = (SELECT MAX(id) FROM assessments)
    """)
    print(f"  CSFScores         : {len(sheets['CSFScores'])} rows")

    sheets["ControlGaps"] = get_table_df(conn, """
        SELECT function_name, gap_description, priority,
               nist_ref, iso27001_ref, soc2_ref
        FROM control_gaps
        WHERE assessment_id = (SELECT MAX(id) FROM assessments)
    """)
    print(f"  ControlGaps       : {len(sheets['ControlGaps'])} rows")

    sheets["VendorAssessments"] = get_table_df(conn, """
        SELECT vendor_name, service_type, criticality, risk_tier,
               score, gap_count, critical_gaps, assessor, assessment_date
        FROM vendor_assessments
        WHERE id IN (SELECT MAX(id) FROM vendor_assessments GROUP BY vendor_name)
    """)
    print(f"  VendorAssessments : {len(sheets['VendorAssessments'])} rows")

    sheets["VendorTierSummary"] = get_table_df(conn, """
        SELECT risk_tier, COUNT(*) as vendor_count
        FROM vendor_assessments
        WHERE id IN (SELECT MAX(id) FROM vendor_assessments GROUP BY vendor_name)
        GROUP BY risk_tier
    """)
    print(f"  VendorTierSummary : {len(sheets['VendorTierSummary'])} rows")

    conn.close()

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        for name, df in sheets.items():
            if df.empty:
                df = pd.DataFrame({"note": ["No data yet - run the relevant module first"]})
            df.to_excel(writer, sheet_name=name, index=False)

            # Format each sheet as a real Excel Table so Power BI can read it
            ws       = writer.sheets[name]
            n_rows   = len(df) + 1                       # data rows + header row
            last_col = get_column_letter(len(df.columns))
            ref      = f"A1:{last_col}{n_rows}"
            table    = Table(displayName=f"{name}_tbl", ref=ref)
            table.tableStyleInfo = TableStyleInfo(
                name="TableStyleMedium2", showRowStripes=True
            )
            ws.add_table(table)

    print(f"\n✅ Exported to: dashboards/grc_powerbi_data.xlsx")
    print("   Upload this file to Power BI at app.powerbi.com")


if __name__ == "__main__":
    main()