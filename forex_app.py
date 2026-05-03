import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Forex Funnel Analysis", layout="wide")

st.title("📊 Forex Transaction Funnel Analysis (Real Data)")

# Load data
df = pd.read_csv("final_forex_dataset.csv")

# ----------------------------
# 🔍 SIDEBAR FILTERS
# ----------------------------
st.sidebar.header("Filters")

customer_type = st.sidebar.selectbox(
    "Customer Type", ["All"] + list(df["customer_type"].unique())
)

channel = st.sidebar.selectbox(
    "Channel", ["All"] + list(df["channel"].unique())
)

txn_amount = st.sidebar.multiselect(
    "Transaction Amount",
    options=sorted(df["txn_amount"].unique()),
    default=sorted(df["txn_amount"].unique())
)

filtered_df = df.copy()

if customer_type != "All":
    filtered_df = filtered_df[filtered_df["customer_type"] == customer_type]

if channel != "All":
    filtered_df = filtered_df[filtered_df["channel"] == channel]

filtered_df = filtered_df[filtered_df["txn_amount"].isin(txn_amount)]

# ----------------------------
# 📊 FUNNEL METRICS
# ----------------------------
funnel = filtered_df.groupby("stage")["user_id"].nunique().reset_index()

funnel = funnel.sort_values(by="stage")

# Conversion %
funnel["conversion_pct"] = (funnel["user_id"] / funnel.iloc[0]["user_id"]) * 100

# Drop-off
funnel["drop_off"] = funnel["user_id"].shift(1) - funnel["user_id"]

# KPIs
total_users = funnel.iloc[0]["user_id"]
completed_users = funnel.iloc[-1]["user_id"]
conversion_rate = round((completed_users / total_users) * 100, 2)

col1, col2, col3 = st.columns(3)
col1.metric("Total Users", total_users)
col2.metric("Completed Transactions", completed_users)
col3.metric("Conversion Rate (%)", conversion_rate)

# ----------------------------
# 🔻 FUNNEL CHART
# ----------------------------
st.subheader("User Funnel")

fig = px.funnel(funnel, x="user_id", y="stage")
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# 📉 DROP-OFF TABLE
# ----------------------------
st.subheader("Stage-wise Conversion & Drop-off")
st.dataframe(funnel)

# ----------------------------
# 🔍 SMART INSIGHTS
# ----------------------------
st.subheader("🔍 Product Insights")

max_drop_stage = funnel.loc[funnel["drop_off"].idxmax()]["stage"]

st.write(f"⚠️ Highest drop-off occurs at: **{max_drop_stage}**")

if max_drop_stage == "KYC Completed":
    st.warning("High friction at KYC → simplify onboarding or reduce documentation")

elif max_drop_stage == "Initiated":
    st.warning("Users dropping early → improve landing experience & clarity")

elif max_drop_stage == "Completed":
    st.warning("Final step failures → possible payment or system issues")

if conversion_rate < 40:
    st.error("🚨 Overall conversion is low → optimize funnel stages urgently")
else:
    st.success("✅ Funnel performance looks healthy")

# ----------------------------
# 📊 CUSTOMER SEGMENT ANALYSIS
# ----------------------------
st.subheader("👥 New vs Repeat User Behavior")

segment = filtered_df.groupby(["customer_type", "stage"])["user_id"].nunique().reset_index()

fig2 = px.line(segment, x="stage", y="user_id", color="customer_type", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# 📱 CHANNEL PERFORMANCE
# ----------------------------
st.subheader("📱 Channel Performance")

channel_perf = filtered_df.groupby(["channel", "stage"])["user_id"].nunique().reset_index()

fig3 = px.bar(channel_perf, x="stage", y="user_id", color="channel", barmode="group")
st.plotly_chart(fig3, use_container_width=True)

# ----------------------------
# ⏱️ TAT ANALYSIS
# ----------------------------
st.subheader("⏱️ Turnaround Time (TAT) Impact")

tat = filtered_df.groupby("stage")["tat_minutes"].mean().reset_index()

fig4 = px.bar(tat, x="stage", y="tat_minutes")
st.plotly_chart(fig4, use_container_width=True)

# ----------------------------
# 📌 FINAL TAKEAWAYS
# ----------------------------
st.subheader("📌 Key Takeaways")

st.write("""
- Identify bottlenecks using drop-off stages  
- Compare behavior across customer segments  
- Evaluate channel effectiveness  
- Link operational delays (TAT) to conversion loss  
""")
