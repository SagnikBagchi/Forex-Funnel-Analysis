import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Forex Funnel Analysis", layout="wide")

st.title("📊 Forex Transaction Funnel Analysis")

df = pd.read_csv("final_forex_dataset.csv")

# Sidebar filters
st.sidebar.header("Filters")

customer_type = st.sidebar.selectbox("Customer Type", ["All"] + list(df["customer_type"].unique()))
channel = st.sidebar.selectbox("Channel", ["All"] + list(df["channel"].unique()))

filtered_df = df.copy()

if customer_type != "All":
    filtered_df = filtered_df[filtered_df["customer_type"] == customer_type]

if channel != "All":
    filtered_df = filtered_df[filtered_df["channel"] == channel]

# Funnel Data
funnel = filtered_df.groupby("stage")["user_id"].nunique().reset_index()

# KPIs
total_users = funnel.iloc[0]["user_id"]
completed_users = funnel.iloc[-1]["user_id"]
conversion_rate = round((completed_users / total_users) * 100, 2)

col1, col2, col3 = st.columns(3)
col1.metric("Total Users", total_users)
col2.metric("Completed Transactions", completed_users)
col3.metric("Conversion Rate (%)", conversion_rate)

# Funnel Chart
st.subheader("User Funnel")
fig = px.funnel(funnel, x="user_id", y="stage")
st.plotly_chart(fig, use_container_width=True)

# Drop-off
st.subheader("Drop-off Analysis")
funnel["drop_off"] = funnel["user_id"].diff(-1).fillna(0)
st.dataframe(funnel)

# TAT Analysis
st.subheader("Average Turnaround Time (TAT)")
tat = filtered_df.groupby("stage")["tat_minutes"].mean().reset_index()
fig2 = px.bar(tat, x="stage", y="tat_minutes")
st.plotly_chart(fig2, use_container_width=True)

# Insights
st.subheader("🔍 Product Insights")

st.write("""
- High drop at KYC stage → simplify documentation  
- Drop at Quote stage → improve FX transparency  
- Drop at Beneficiary stage → UX friction  
- High TAT → process inefficiency  
""")
