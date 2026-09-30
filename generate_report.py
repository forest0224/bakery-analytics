"""
generate_report.py
Generates Project_Report.docx from bakery churn data.
Run: python generate_report.py
"""

import pandas as pd
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from datetime import date


# ── Load data ─────────────────────────────────────────────────────────────────
churn_df = pd.read_csv("bakery_churn_dashboard_data.csv")
churn_df["Churn_Probability"] = pd.to_numeric(churn_df["Churn_Probability"], errors="coerce")
churn_df["Monetary"] = pd.to_numeric(churn_df["Monetary"], errors="coerce")

def assign_risk(prob):
    if prob >= 70:
        return "High Risk"
    elif prob >= 30:
        return "Medium Risk"
    else:
        return "Low Risk"

if "Risk_Level" not in churn_df.columns:
    churn_df["Risk_Level"] = churn_df["Churn_Probability"].apply(assign_risk)

txn_df = pd.read_excel("bakery_synthetic_dataset.csv (1).xlsx")

# ── Computed metrics ──────────────────────────────────────────────────────────
total_customers   = len(churn_df)
high_risk_count   = int((churn_df["Risk_Level"] == "High Risk").sum())
medium_risk_count = int((churn_df["Risk_Level"] == "Medium Risk").sum())
low_risk_count    = int((churn_df["Risk_Level"] == "Low Risk").sum())
avg_churn_prob    = churn_df["Churn_Probability"].mean()
at_risk_revenue   = churn_df.loc[churn_df["Risk_Level"] == "High Risk", "Monetary"].sum()
total_transactions = len(txn_df)

# ── Helper functions ──────────────────────────────────────────────────────────
def add_heading(doc, text, level=1, color=None):
    heading = doc.add_heading(text, level=level)
    run = heading.runs[0] if heading.runs else heading.add_run(text)
    if color:
        run.font.color.rgb = RGBColor(*color)
    return heading


def add_paragraph(doc, text, bold=False, size=11):
    para = doc.add_paragraph()
    run = para.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    return para


def add_styled_table(doc, headers, rows, header_color=(59, 130, 212)):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        cell = hdr_cells[i]
        cell.text = h
        run = cell.paragraphs[0].runs[0]
        run.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)
        run.font.size = Pt(10)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        tc_pr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "{:02X}{:02X}{:02X}".format(*header_color))
        shd.set(qn("w:val"), "clear")
        tc_pr.append(shd)

    # Data rows
    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            row_cells[c_idx].paragraphs[0].runs[0].font.size = Pt(10)

    return table


# ── Build Document ────────────────────────────────────────────────────────────
doc = Document()

# Title
title = doc.add_heading("Bakery Customer Churn Analytics", 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.runs[0].font.color.rgb = RGBColor(30, 64, 175)

sub = doc.add_paragraph(f"Project Report  ·  Generated: {date.today().strftime('%B %d, %Y')}")
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub.runs[0].font.color.rgb = RGBColor(107, 114, 128)
doc.add_paragraph()

# ── 1. Executive Summary ──────────────────────────────────────────────────────
add_heading(doc, "1. Executive Summary", level=1, color=(30, 64, 175))
doc.add_paragraph(
    "Customer churn is one of the most significant threats to sustained revenue in a competitive bakery market. "
    "This project builds a data-driven churn risk prevention framework using RFM (Recency, Frequency, Monetary) "
    "analytics and an XGBoost gradient-boosted classification model. By scoring every customer with a churn "
    "probability and assigning a Risk Level tier, the business can allocate retention budget efficiently — "
    "focusing intensive win-back campaigns on High-Risk customers while nurturing Medium and Low-Risk segments "
    "through loyalty programmes and personalised promotions."
)
doc.add_paragraph(
    "The interactive Streamlit dashboard provides real-time visibility into churn risk across the customer base, "
    "supports drill-down into individual purchase histories, and enables data exports for offline CRM workflows."
)
doc.add_paragraph()

# ── 2. Dataset & Methodology ──────────────────────────────────────────────────
add_heading(doc, "2. Dataset & Methodology", level=1, color=(30, 64, 175))

add_heading(doc, "2.1  Data Sources", level=2)
add_styled_table(
    doc,
    headers=["File", "Rows", "Columns", "Role"],
    rows=[
        ["bakery_synthetic_dataset.csv (1).xlsx",
         f"{total_transactions:,}", "41",
         "Raw transaction log — source of RFM feature engineering"],
        ["bakery_churn_dashboard_data.csv",
         f"{total_customers:,}", "8",
         "Pre-computed XGBoost model outputs (RFM features + risk scores)"],
    ],
    header_color=(30, 64, 175),
)
doc.add_paragraph()

add_heading(doc, "2.2  RFM Feature Definitions", level=2)
add_styled_table(
    doc,
    headers=["Feature", "Formula / Definition", "Business Meaning"],
    rows=[
        ["Recency",        "Days since last purchase (as of cut-off date)",
         "How recently the customer engaged"],
        ["Frequency",      "Count of distinct transactions in observation window",
         "How often the customer visits"],
        ["Monetary",       "Sum of Total_Bill in observation window (₹)",
         "How much the customer spends"],
        ["Avg_Order_Value","Monetary ÷ Frequency",
         "Average basket size per visit"],
    ],
)
doc.add_paragraph()

add_heading(doc, "2.3  Leakage-Safe Historical Split", level=2)
doc.add_paragraph(
    "To prevent data leakage, a hard date cut-off is applied before computing RFM features. "
    "Transactions after the cut-off date are used exclusively to derive the ground-truth churn label "
    "(whether the customer returned). Training features are computed only on pre-cut-off data. "
    "An XGBoost classifier is then trained on the resulting feature matrix with cross-validated "
    "hyperparameter tuning, producing a calibrated churn probability between 0 % and 100 % for each customer."
)
doc.add_paragraph()

# ── 3. Key Data Insights ──────────────────────────────────────────────────────
add_heading(doc, "3. Key Data Insights", level=1, color=(30, 64, 175))
add_styled_table(
    doc,
    headers=["Metric", "Value"],
    rows=[
        ["Total Customers Scored",     f"{total_customers:,}"],
        ["High-Risk Customers (≥70 %)", f"{high_risk_count:,}  ({high_risk_count/total_customers*100:.1f} %)"],
        ["Medium-Risk Customers",       f"{medium_risk_count:,}  ({medium_risk_count/total_customers*100:.1f} %)"],
        ["Low-Risk Customers (<30 %)",  f"{low_risk_count:,}  ({low_risk_count/total_customers*100:.1f} %)"],
        ["Average Churn Probability",   f"{avg_churn_prob:.1f} %"],
        ["Total At-Risk Revenue (High)", f"₹{at_risk_revenue:,.2f}"],
        ["Total Raw Transactions",      f"{total_transactions:,}"],
    ],
)
doc.add_paragraph()

# ── 4. Business Retention Strategies ─────────────────────────────────────────
add_heading(doc, "4. Business Retention Strategies", level=1, color=(30, 64, 175))
doc.add_paragraph(
    "The following targeted campaigns are recommended based on each customer's risk tier. "
    "Interventions are ordered by urgency — High-Risk actions should be triggered within 7 days."
)
doc.add_paragraph()
add_styled_table(
    doc,
    headers=["Risk Tier", "Churn Probability", "Recommended Actions", "Priority"],
    rows=[
        ["🔴 High Risk",   "≥ 70 %",
         "Personalised win-back discount (15–20 %) · Loyalty point acceleration · "
         "Direct manager outreach for top spenders · Urgency push notification within 7 days",
         "Immediate"],
        ["🟠 Medium Risk", "30 – 69 %",
         "Cross-sell bundle promotions (10 % off) · Seasonal & festival campaigns · "
         "Communicate loyalty tier upgrade progress",
         "Within 30 days"],
        ["🟢 Low Risk",    "< 30 %",
         "Referral programme with store credit · Premium product early access · "
         "Weekly bread subscription box offer",
         "Ongoing"],
    ],
    header_color=(30, 64, 175),
)
doc.add_paragraph()

# Footer note
doc.add_paragraph()
footer_para = doc.add_paragraph(
    "Bakery Customer Churn Analytics  ·  Powered by XGBoost & Streamlit  ·  "
    f"Report generated on {date.today().strftime('%B %d, %Y')}"
)
footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer_para.runs[0].font.color.rgb = RGBColor(107, 114, 128)
footer_para.runs[0].font.size = Pt(9)

# ── Save ──────────────────────────────────────────────────────────────────────
doc.save("Project_Report.docx")
print("Project_Report.docx saved successfully.")
