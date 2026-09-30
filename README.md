# 🥖 Bakery Customer Churn Dashboard & Analytics

## Project Overview

This project delivers an end-to-end **customer churn prediction and risk segmentation system** for a bakery business. Using RFM (Recency, Frequency, Monetary) features derived from historical transaction data, an XGBoost classification model assigns every customer a churn probability score and risk tier (High / Medium / Low). The results are surfaced through an interactive **Streamlit dashboard** so business stakeholders can monitor retention risk, drill into individual customer histories, and export filtered reports — all without running any ML code.

---

## Repository Structure

```
project 1/
├── app.py                              # Streamlit dashboard (main entry point)
├── generate_report.py                  # Word document report generator
├── requirements.txt                    # Pinned Python dependencies
├── bakery_churn_dashboard_data.csv     # Pre-computed model outputs (RFM + risk scores)
├── bakery_synthetic_dataset.csv (1).xlsx  # Raw transaction log (16 570 rows × 41 cols)
├── Jaydeep_BakeryAnalytics (1).ipynb   # Model training & feature engineering notebook
└── README.md                           # This file
```

---

## Dataset Structure

### `bakery_churn_dashboard_data.csv` — Model Risk Outputs
Pre-computed predictions produced by the XGBoost model. Used by both the dashboard and the Word report generator.

| Column | Description |
|---|---|
| `Customer_ID` | Unique customer identifier (e.g. `CUST00783`) |
| `Recency` | Days since the customer's last purchase |
| `Frequency` | Number of transactions in the observation window |
| `Monetary` | Total spend (₹) in the observation window |
| `Avg_Order_Value` | `Monetary / Frequency` |
| `Actual_Churn` | Ground-truth churn label (0 = retained, 1 = churned) |
| `Predicted_Churn` | Model binary prediction |
| `Churn_Probability` | Model churn probability score (0–100 %) |
| `Risk_Level` | Derived tier: **High Risk** (≥70 %), **Medium Risk** (30–69 %), **Low Risk** (<30 %) |

### `bakery_synthetic_dataset.csv (1).xlsx` — Raw Transaction Log
Full granular transaction history used for customer drill-down in the dashboard.

| Column Group | Examples |
|---|---|
| Transaction meta | `Transaction_ID`, `Date`, `Time` |
| Customer profile | `Customer_ID`, `Customer_Age`, `Customer_Gender`, `Customer_Segment`, `Loyalty_Member` |
| Product details | `Product`, `Category`, `Quantity`, `Unit_Price`, `Selling_Price`, `Total_Bill` |
| Operational | `Store_ID`, `Employee_ID`, `Payment_Method`, `Weather`, `Season`, `Festival` |
| Inventory & waste | `Stock_Available`, `Units_Produced`, `Unsold_Units`, `Expiry_Risk`, `Waste_Cost` |
| Promotions | `Promotion_Applied`, `Promotion_Type`, `Promotion_Score` |
| Recommendations | `Recommended_Product`, `Recommended_Discount` |

---

## Setup & Run Instructions

### 1 — Clone / download the project
```
cd "path/to/project 1"
```

### 2 — Create a virtual environment (recommended)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### 4 — Launch the dashboard
```bash
streamlit run app.py
```
The app opens automatically at **http://localhost:8501**.

### 5 — Generate the Word report (optional)
```bash
python generate_report.py
```
Outputs `Project_Report.docx` in the project root.

---

## Dashboard Features

| Feature | Details |
|---|---|
| **Sidebar Filters** | Filter by Risk Level (All / High / Medium / Low) and a Churn Probability range slider (0–100 %) |
| **KPI Summary Cards** | Total Filtered Customers · High-Risk Count · Average Churn Probability · Total At-Risk Revenue |
| **Donut Chart** | Customer distribution across the three risk tiers |
| **Scatter Plot** | Recency vs. Churn Probability coloured by Risk Level; hover reveals Customer ID, Frequency, Monetary |
| **Bar Chart** | Top 10 High-Risk customers ranked by Monetary spend, shaded by Churn Probability |
| **Customer Drill-Down** | Select any Customer ID to view their predicted risk profile alongside their full transaction history |
| **Filtered Data Table** | Sortable, searchable table of all filtered customers with a one-click CSV export |

---

## Business Retention Recommendations

### 🔴 High Risk (Churn Probability ≥ 70 %)
- **Personalised win-back campaigns**: send targeted discounts (15–20 %) on their most purchased product categories.
- **Loyalty acceleration**: offer double loyalty points for the next 3 purchases to re-establish buying habits.
- **Direct outreach**: high-value High-Risk customers (top Monetary) should receive a personal call or WhatsApp message from the store manager.
- **Urgency nudge**: "We miss you — your favourite [Product] is waiting" push notification within 7 days of no purchase.

### 🟠 Medium Risk (Churn Probability 30–69 %)
- **Bundle promotions**: offer cross-sell bundles (e.g. bread + pastry combo) at a 10 % discount to increase basket size and visit frequency.
- **Seasonal campaigns**: target Medium-Risk customers during festivals and weekends when purchase propensity is higher.
- **Loyalty tier upgrade**: communicate how close they are to the next loyalty tier to motivate more frequent visits.

### 🟢 Low Risk (Churn Probability < 30 %)
- **Referral programme**: satisfied, low-risk customers are the best brand advocates — incentivise referrals with store credit.
- **Premium product introductions**: introduce new or premium items to this segment first to drive trial and maintain engagement.
- **Subscription / pre-order options**: offer weekly bread subscription boxes to lock in recurring revenue from your most loyal customers.

---

## Technical Notes

- **No ML re-training at runtime** — the dashboard reads pre-computed predictions only, keeping startup fast and resource-light.
- **Leakage-safe split** — the training notebook uses a historical date cut-off to prevent future data from leaking into RFM features.
- **Churn definition** — a customer is labelled churned if they have not purchased within a configurable recency threshold after the observation window.

---

*Bakery Customer Churn Analytics · Built with Streamlit, Plotly, pandas & XGBoost*
