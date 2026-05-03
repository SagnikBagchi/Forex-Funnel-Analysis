import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Funnel Analytics Dashboard", layout="wide")

# ----------------------------
# HEADER
# ----------------------------
st.title("Customer Funnel Analytics")
st.caption("Understand user behavior, conversion, and business impact across the funnel")

# ----------------------------
# LOAD DATA
# ----------------------------
uploaded_file = st.sidebar.file_uploader("Upload Dataset", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("final_forex_dataset.csv")

df = df.rename(columns={
    "customer_type": "Customer Type",
    "channel": "Channel",
    "txn_amount": "Transaction Amount",
    "tat_minutes": "Processing Time",
    "user_id": "User ID",
    "stage": "Stage"
})

# ----------------------------
# FILTERS
# ----------------------------
st.sidebar.header("Filters")

def create_filter(col):
    vals = sorted(df[col].dropna().unique())
    return st.sidebar.multiselect(col, vals, default=vals)

filters = {}
for col in ["Customer Type", "Channel", "Transaction Amount"]:
    if col in df.columns:
        filters[col] = create_filter(col)

filtered_df = df.copy()
for col, val in filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(val)]

# ----------------------------
# FUNNEL LOGIC
# ----------------------------
funnel = filtered_df.groupby("Stage")["User ID"].nunique().reset_index()

if funnel.empty:
    st.warning("No data available for selected filters.")
    st.stop()

order = ["Initiated", "KYC Completed", "Completed"]
if set(order).issubset(set(funnel["Stage"])):
    funnel["Stage"] = pd.Categorical(funnel["Stage"], categories=order, ordered=True)

funnel = funnel.sort_values("Stage").reset_index(drop=True)
funnel["User ID"] = funnel["User ID"].cummin()

base = funnel.iloc[0]["User ID"]

funnel["Conversion %"] = (funnel["User ID"] / base) * 100
funnel["Drop %"] = (funnel["User ID"].shift(1) - funnel["User ID"]) / funnel["User ID"].shift(1) * 100
funnel = funnel.fillna(0)

# ----------------------------
# SECTION 1: OVERVIEW
# ----------------------------
st.markdown("## Overview")

col1, col2, col3 = st.columns(3)

total = base
completed = funnel.iloc[-1]["User ID"]
conversion = round((completed / total) * 100, 2)

col1.metric("Total Users", total)
col2.metric("Completed", completed)
col3.metric("Conversion Rate", f"{conversion}%")

col1, col2 = st.columns([2,1])

with col1:
    fig = px.funnel(funnel, x="User ID", y="Stage")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.dataframe(funnel[["Stage", "User ID", "Conversion %", "Drop %"]])

# ----------------------------
# SECTION 2: DIAGNOSTICS
# ----------------------------
st.markdown("## Where are users dropping?")

max_idx = funnel["Drop %"].idxmax()
problem_stage = funnel.loc[max_idx, "Stage"]
drop_value = round(funnel.loc[max_idx, "Drop %"], 2)

st.info(f"Highest drop-off occurs at {problem_stage} ({drop_value}%)")

col1, col2 = st.columns(2)

# Segment comparison
if "Customer Type" in filtered_df.columns:
    seg = filtered_df.groupby(["Customer Type", "Stage"])["User ID"].nunique().reset_index()
    fig2 = px.line(seg, x="Stage", y="User ID", color="Customer Type", markers=True)
    col1.plotly_chart(fig2, use_container_width=True)

# Channel comparison
if "Channel" in filtered_df.columns:
    ch = filtered_df.groupby(["Channel", "Stage"])["User ID"].nunique().reset_index()
    fig3 = px.bar(ch, x="Stage", y="User ID", color="Channel", barmode="group")
    col2.plotly_chart(fig3, use_container_width=True)

# ----------------------------
# SECTION 3: WHY IS THIS HAPPENING
# ----------------------------
st.markdown("## Why is this happening?")

col1, col2 = st.columns(2)

# Transaction value
if "Transaction Amount" in filtered_df.columns:
    fig4 = px.box(filtered_df, x="Stage", y="Transaction Amount")
    col1.plotly_chart(fig4, use_container_width=True)

# Processing time
if "Processing Time" in filtered_df.columns:
    tat = filtered_df.groupby("Stage")["Processing Time"].mean().reset_index()
    fig5 = px.bar(tat, x="Stage", y="Processing Time")
    col2.plotly_chart(fig5, use_container_width=True)

# ----------------------------
# SECTION 4: RECOMMENDATIONS
# ----------------------------
st.markdown("## What should we do?")

if drop_value > 50:
    st.write("- Simplify process at critical stage")
    st.write("- Remove friction and reduce steps")
elif drop_value > 30:
    st.write("- Optimize user experience at drop-off stage")
    st.write("- Improve clarity and reduce confusion")
else:
    st.write("- Funnel is stable, focus on incremental improvements")

if "Processing Time" in filtered_df.columns:
    st.write("- Reduce processing delays to improve conversion")

if "Customer Type" in filtered_df.columns:
    st.write("- Improve onboarding for new users")

if "Channel" in filtered_df.columns:
    st.write("- Focus on improving lower-performing channels")

# ----------------------------
# SECTION 5: SUMMARY
# ----------------------------
st.markdown("## Executive Summary")

st.write(f"""
- Conversion Rate: {conversion}%
- Main drop-off: {problem_stage}
- Focus area: improving user experience at critical stages
""")
