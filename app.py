"""
Bakery Customer Churn Analytics Dashboard
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bakery Churn Analytics",
    page_icon="🥖",
    layout="wide",
)

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_dashboard_data() -> pd.DataFrame:
    df = pd.read_csv("bakery_churn_dashboard_data.csv")
    df["Churn_Probability"] = pd.to_numeric(df["Churn_Probability"], errors="coerce")
    df["Monetary"] = pd.to_numeric(df["Monetary"], errors="coerce")
    df["Recency"] = pd.to_numeric(df["Recency"], errors="coerce")
    df["Frequency"] = pd.to_numeric(df["Frequency"], errors="coerce")

    # Derive Risk_Level from Churn_Probability (0–100 scale)
    def assign_risk(prob):
        if prob >= 70:
            return "High Risk"
        elif prob >= 30:
            return "Medium Risk"
        else:
            return "Low Risk"

    if "Risk_Level" not in df.columns:
        df["Risk_Level"] = df["Churn_Probability"].apply(assign_risk)
    return df


@st.cache_data
def load_transaction_data() -> pd.DataFrame:
    # The raw data is an xlsx file
    return pd.read_excel("bakery_synthetic_dataset.csv (1).xlsx")


churn_df = load_dashboard_data()
txn_df = load_transaction_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
st.sidebar.title("🔍 Filters")

risk_options = ["All", "High Risk", "Medium Risk", "Low Risk"]
selected_risk = st.sidebar.selectbox("Risk Level", risk_options)

prob_min, prob_max = st.sidebar.slider(
    "Churn Probability (%)",
    min_value=0,
    max_value=100,
    value=(0, 100),
    step=1,
)

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = churn_df.copy()
if selected_risk != "All":
    filtered = filtered[filtered["Risk_Level"] == selected_risk]
filtered = filtered[
    (filtered["Churn_Probability"] >= prob_min)
    & (filtered["Churn_Probability"] <= prob_max)
]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🥖 Bakery Customer Churn Analytics Dashboard")
st.markdown("Real-time churn risk overview powered by XGBoost RFM predictions.")
st.divider()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total_customers = len(filtered)
high_risk_count = int((filtered["Risk_Level"] == "High Risk").sum())
avg_churn_prob = filtered["Churn_Probability"].mean() if total_customers > 0 else 0.0
at_risk_revenue = filtered.loc[
    filtered["Risk_Level"] == "High Risk", "Monetary"
].sum()

k1, k2, k3, k4 = st.columns(4)
k1.metric("👥 Total Filtered Customers", f"{total_customers:,}")
k2.metric("🔴 High-Risk Customers", f"{high_risk_count:,}")
k3.metric("📊 Avg Churn Probability", f"{avg_churn_prob:.1f}%")
k4.metric("💰 Total At-Risk Revenue", f"₹{at_risk_revenue:,.2f}")

st.divider()

# ── Visualisations ────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 2])

# Donut chart – Risk Level distribution
with col_left:
    st.subheader("Customer Risk Distribution")
    risk_counts = filtered["Risk_Level"].value_counts().reset_index()
    risk_counts.columns = ["Risk_Level", "Count"]
    color_map = {"High Risk": "#ef4444", "Medium Risk": "#f97316", "Low Risk": "#22c55e"}
    fig_donut = px.pie(
        risk_counts,
        names="Risk_Level",
        values="Count",
        hole=0.55,
        color="Risk_Level",
        color_discrete_map=color_map,
        title="Risk Level Breakdown",
    )
    fig_donut.update_traces(textposition="inside", textinfo="percent+label")
    fig_donut.update_layout(showlegend=True, margin=dict(t=40, b=20, l=0, r=0))
    st.plotly_chart(fig_donut, use_container_width=True)

# Scatter – Recency vs Churn_Probability
with col_right:
    st.subheader("Recency vs. Churn Probability")
    fig_scatter = px.scatter(
        filtered,
        x="Recency",
        y="Churn_Probability",
        color="Risk_Level",
        color_discrete_map=color_map,
        hover_data=["Customer_ID", "Frequency", "Monetary"],
        labels={
            "Recency": "Recency (days since last purchase)",
            "Churn_Probability": "Churn Probability (%)",
        },
        title="Recency vs. Churn Probability by Risk Level",
    )
    fig_scatter.update_traces(marker=dict(size=6, opacity=0.75))
    fig_scatter.update_layout(margin=dict(t=40, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

# Bar chart – Top 10 High-Risk Customers by Monetary
st.subheader("Top 10 High-Risk Customers by Monetary Spend")
top10 = (
    filtered[filtered["Risk_Level"] == "High Risk"]
    .nlargest(10, "Monetary")
    .reset_index(drop=True)
)
if not top10.empty:
    fig_bar = px.bar(
        top10,
        x="Customer_ID",
        y="Monetary",
        color="Churn_Probability",
        color_continuous_scale=["#fde68a", "#ef4444"],
        labels={"Monetary": "Total Spend (₹)", "Customer_ID": "Customer ID"},
        title="Top 10 High-Risk Customers – Monetary Value",
        text_auto=".2f",
    )
    fig_bar.update_layout(xaxis_tickangle=-30, margin=dict(t=40, b=60))
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No High-Risk customers match the current filters.")

st.divider()

# ── Customer Search & Drill-Down ──────────────────────────────────────────────
st.subheader("🔎 Customer Search & Drill-Down")

customer_ids = sorted(churn_df["Customer_ID"].dropna().unique().tolist())
selected_customer = st.selectbox("Select Customer ID", ["— select —"] + customer_ids)

if selected_customer != "— select —":
    cust_row = churn_df[churn_df["Customer_ID"] == selected_customer]

    st.markdown("#### Predicted Risk Profile")
    if not cust_row.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Churn Probability", f"{cust_row['Churn_Probability'].values[0]:.1f}%")
        c2.metric("Risk Level", cust_row["Risk_Level"].values[0])
        c3.metric("Recency (days)", int(cust_row["Recency"].values[0]))
        c4.metric("Frequency", int(cust_row["Frequency"].values[0]))
        st.dataframe(cust_row.reset_index(drop=True), use_container_width=True)
    else:
        st.warning("Customer not found in predictions data.")

    st.markdown("#### Past Transaction History")
    cust_txns = txn_df[txn_df["Customer_ID"] == selected_customer]
    if not cust_txns.empty:
        st.dataframe(
            cust_txns.reset_index(drop=True),
            use_container_width=True,
            height=300,
        )
    else:
        st.info("No transaction records found for this customer.")

st.divider()

# ── Interactive Filtered Table ────────────────────────────────────────────────
st.subheader("📋 Filtered Customer Table")
st.dataframe(
    filtered.reset_index(drop=True),
    use_container_width=True,
    height=400,
)

csv_export = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Filtered Results as CSV",
    data=csv_export,
    file_name="filtered_churn_results.csv",
    mime="text/csv",
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    "<hr style='margin-top:2rem'><p style='text-align:center;color:#6b7280;font-size:0.8rem;'>"
    "Bakery Churn Analytics Dashboard · Powered by Streamlit & XGBoost RFM Model</p>",
    unsafe_allow_html=True,
)
