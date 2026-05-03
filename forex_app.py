import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# ⚙️ PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Funnel Analytics Dashboard", layout="wide")

st.title("📊 Product Funnel Analytics Dashboard")

# ----------------------------
# 📥 DATA LOADING
# ----------------------------
uploaded_file = st.sidebar.file_uploader("Upload your dataset (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("final_forex_dataset.csv")

# ----------------------------
# 🔍 FILTERS (AUTO)
# ----------------------------
st.sidebar.header("Filters")

def create_filter(column):
    values = df[column].dropna().unique()
    return st.sidebar.multiselect(column, values, default=values)

filters = {}
for col in ["customer_type", "channel", "txn_amount"]:
    if col in df.columns:
        filters[col] = create_filter(col)

filtered_df = df.copy()

for col, selected in filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected)]

# ----------------------------
# 📊 FUNNEL CALCULATION
# ----------------------------
funnel = filtered_df.groupby("stage")["user_id"].nunique().reset_index()

if funnel.empty:
    st.error("No data available for selected filters.")
    st.stop()

# Maintain logical order
stage_order = ["Initiated", "KYC Completed", "Completed"]
if set(stage_order).issubset(set(funnel["stage"])):
    funnel["stage"] = pd.Categorical(funnel["stage"], categories=stage_order, ordered=True)

funnel = funnel.sort_values("stage").reset_index(drop=True)

# ----------------------------
# 🔥 FIX: MONOTONIC FUNNEL ENFORCEMENT
# ----------------------------
funnel["user_id"] = funnel["user_id"].cummin()

# Metrics
base_users = funnel.iloc[0]["user_id"]

funnel["conversion_pct"] = (funnel["user_id"] / base_users) * 100

funnel["drop_off"] = funnel["user_id"].shift(1) - funnel["user_id"]
funnel["drop_pct"] = (funnel["drop_off"] / funnel["user_id"].shift(1)) * 100

# Clean NaN
funnel = funnel.fillna(0)

# ----------------------------
# 📊 KPIs
# ----------------------------
total_users = base_users
completed_users = funnel.iloc[-1]["user_id"]
conversion_rate = round((completed_users / total_users) * 100, 2)

col1, col2, col3 = st.columns(3)
col1.metric("Total Users", total_users)
col2.metric("Conversion Rate (%)", conversion_rate)
col3.metric("Completed Users", completed_users)

# ----------------------------
# 🔻 FUNNEL CHART
# ----------------------------
st.subheader("User Funnel")

fig = px.funnel(funnel, x="user_id", y="stage")
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# 📉 FUNNEL TABLE
# ----------------------------
st.subheader("Stage-wise Performance")
st.dataframe(funnel)

# ----------------------------
# 🔍 INSIGHTS
# ----------------------------
st.subheader("🔍 Automated Insights")

max_drop_idx = funnel["drop_pct"].idxmax()
max_drop_stage = funnel.loc[max_drop_idx, "stage"]
max_drop_value = funnel.loc[max_drop_idx, "drop_pct"]

st.write(f"⚠️ Highest drop-off: **{round(max_drop_value,2)}% at {max_drop_stage}**")

if max_drop_value > 50:
    st.error("🚨 Severe drop-off → immediate action required")
elif max_drop_value > 30:
    st.warning("⚠️ Moderate drop-off → optimize flow")
else:
    st.success("✅ Funnel looks healthy")

# ----------------------------
# 💰 REVENUE IMPACT
# ----------------------------
if "txn_amount" in filtered_df.columns:
    avg_value = filtered_df["txn_amount"].mean()
    total_drop_users = funnel["drop_off"].sum()
    revenue_loss = int(avg_value * total_drop_users)

    st.subheader("💰 Revenue Impact")
    st.metric("Estimated Revenue Loss", f"{revenue_loss:,}")

# ----------------------------
# 👥 SEGMENT ANALYSIS
# ----------------------------
if "customer_type" in filtered_df.columns:
    st.subheader("👥 Customer Segment Analysis")

    seg = filtered_df.groupby(["customer_type", "stage"])["user_id"].nunique().reset_index()

    fig2 = px.line(seg, x="stage", y="user_id", color="customer_type", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# 📱 CHANNEL ANALYSIS
# ----------------------------
if "channel" in filtered_df.columns:
    st.subheader("📱 Channel Performance")

    ch = filtered_df.groupby(["channel", "stage"])["user_id"].nunique().reset_index()

    fig3 = px.bar(ch, x="stage", y="user_id", color="channel", barmode="group")
    st.plotly_chart(fig3, use_container_width=True)

# ----------------------------
# ⏱️ TAT ANALYSIS
# ----------------------------
if "tat_minutes" in filtered_df.columns:
    st.subheader("⏱️ TAT Impact")

    tat = filtered_df.groupby("stage")["tat_minutes"].mean().reset_index()

    fig4 = px.bar(tat, x="stage", y="tat_minutes")
    st.plotly_chart(fig4, use_container_width=True)

# ----------------------------
# 📌 TAKEAWAYS
# ----------------------------
st.subheader("📌 Key Takeaways")

st.write(f"""
- Maximum drop-off occurs at **{max_drop_stage}**
- Conversion rate is **{conversion_rate}%**
- Funnel is adjusted for realistic progression
- Focus on optimizing high drop-off stages
""")
