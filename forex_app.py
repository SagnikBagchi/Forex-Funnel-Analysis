import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Funnel Analytics Dashboard", layout="wide")

st.title("Customer Funnel Analytics Dashboard")
st.markdown("End-to-end analysis of customer progression, conversion, and business impact")

# ----------------------------
# LOAD DATA
# ----------------------------
uploaded_file = st.sidebar.file_uploader("Upload Dataset (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("final_forex_dataset.csv")

# ----------------------------
# CLEAN COLUMN NAMES
# ----------------------------
df = df.rename(columns={
    "customer_type": "Customer Type",
    "channel": "Channel",
    "txn_amount": "Transaction Amount",
    "tat_minutes": "Processing Time (mins)",
    "user_id": "User ID",
    "stage": "Stage"
})

# ----------------------------
# FILTERS
# ----------------------------
st.sidebar.header("Filters")

def create_filter(column):
    values = sorted(df[column].dropna().unique())
    return st.sidebar.multiselect(column, values, default=values)

filters = {}
for col in ["Customer Type", "Channel", "Transaction Amount"]:
    if col in df.columns:
        filters[col] = create_filter(col)

filtered_df = df.copy()
for col, selected in filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected)]

# ----------------------------
# FUNNEL CALCULATION
# ----------------------------
funnel = filtered_df.groupby("Stage")["User ID"].nunique().reset_index()

if funnel.empty:
    st.error("No data available for selected filters.")
    st.stop()

stage_order = ["Initiated", "KYC Completed", "Completed"]
if set(stage_order).issubset(set(funnel["Stage"])):
    funnel["Stage"] = pd.Categorical(funnel["Stage"], categories=stage_order, ordered=True)

funnel = funnel.sort_values("Stage").reset_index(drop=True)

# Enforce monotonic funnel
funnel["User ID"] = funnel["User ID"].cummin()

base_users = funnel.iloc[0]["User ID"]

funnel["Conversion (%)"] = (funnel["User ID"] / base_users) * 100
funnel["Drop-Off"] = funnel["User ID"].shift(1) - funnel["User ID"]
funnel["Drop-Off (%)"] = (funnel["Drop-Off"] / funnel["User ID"].shift(1)) * 100
funnel = funnel.fillna(0)

# ----------------------------
# KPI SECTION
# ----------------------------
st.header("Key Metrics")

total_users = base_users
completed_users = funnel.iloc[-1]["User ID"]
conversion_rate = round((completed_users / total_users) * 100, 2)

col1, col2, col3 = st.columns(3)
col1.metric("Total Users", total_users)
col2.metric("Completed Transactions", completed_users)
col3.metric("Conversion Rate (%)", conversion_rate)

# Business metric
if "Transaction Amount" in filtered_df.columns:
    total_value = filtered_df["Transaction Amount"].sum()
    completed_value = filtered_df[filtered_df["Stage"] == "Completed"]["Transaction Amount"].sum()
    value_conversion = round((completed_value / total_value) * 100, 2)

    st.metric("Value Conversion Rate (%)", value_conversion)

# ----------------------------
# FUNNEL + TABLE
# ----------------------------
st.header("Funnel Overview")

col1, col2 = st.columns([2,1])

with col1:
    fig = px.funnel(funnel, x="User ID", y="Stage")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.dataframe(funnel.style.format({
        "Conversion (%)": "{:.2f}",
        "Drop-Off (%)": "{:.2f}"
    }))

# ----------------------------
# SEGMENT FUNNEL
# ----------------------------
st.header("Customer Segment Comparison")

if "Customer Type" in filtered_df.columns:
    segments = filtered_df["Customer Type"].unique()
    cols = st.columns(len(segments))

    for i, seg in enumerate(segments):
        seg_df = filtered_df[filtered_df["Customer Type"] == seg]
        seg_funnel = seg_df.groupby("Stage")["User ID"].nunique().reset_index()
        seg_funnel = seg_funnel.sort_values("Stage")
        seg_funnel["User ID"] = seg_funnel["User ID"].cummin()

        fig = px.funnel(seg_funnel, x="User ID", y="Stage", title=seg)
        cols[i].plotly_chart(fig, use_container_width=True)

# ----------------------------
# CHANNEL PERFORMANCE
# ----------------------------
st.header("Channel Performance")

if "Channel" in filtered_df.columns:
    channel_conv = filtered_df.groupby(["Channel", "Stage"])["User ID"].nunique().reset_index()
    channel_conv["User ID"] = channel_conv.groupby("Channel")["User ID"].cummin()

    final_stage = channel_conv[channel_conv["Stage"] == "Completed"]
    initial_stage = channel_conv[channel_conv["Stage"] == "Initiated"]

    merged = pd.merge(initial_stage, final_stage, on="Channel", suffixes=("_start", "_end"))
    merged["Conversion Rate (%)"] = (merged["User ID_end"] / merged["User ID_start"]) * 100

    fig = px.bar(merged, x="Channel", y="Conversion Rate (%)")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# TRANSACTION VALUE ANALYSIS
# ----------------------------
st.header("Transaction Value Analysis")

if "Transaction Amount" in filtered_df.columns:
    fig = px.box(filtered_df, x="Stage", y="Transaction Amount")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# PROCESSING TIME
# ----------------------------
st.header("Operational Efficiency")

if "Processing Time (mins)" in filtered_df.columns:
    tat = filtered_df.groupby("Stage")["Processing Time (mins)"].mean().reset_index()
    fig = px.bar(tat, x="Stage", y="Processing Time (mins)")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# INSIGHTS + RECOMMENDATIONS
# ----------------------------
st.header("Insights and Recommendations")

max_drop_idx = funnel["Drop-Off (%)"].idxmax()
max_stage = funnel.loc[max_drop_idx, "Stage"]
max_drop = round(funnel.loc[max_drop_idx, "Drop-Off (%)"], 2)

st.subheader("Key Insight")
st.write(f"The highest drop-off occurs at the **{max_stage}** stage with a drop of **{max_drop}%**.")

st.subheader("Recommendations")

if max_drop > 50:
    st.write("- Simplify the user journey at this stage to reduce friction")
    st.write("- Investigate UX or operational bottlenecks immediately")
elif max_drop > 30:
    st.write("- Optimize process flow and reduce unnecessary steps")
    st.write("- Improve communication and clarity for users")
else:
    st.write("- Funnel is stable, focus on incremental improvements")

if "Processing Time (mins)" in filtered_df.columns:
    st.write("- Reduce processing time to improve conversion")

if "Channel" in filtered_df.columns:
    st.write("- Invest in high-performing channels and optimize low-performing ones")

if "Customer Type" in filtered_df.columns:
    st.write("- Improve onboarding for new users to match repeat user performance")

# ----------------------------
# FINAL SUMMARY
# ----------------------------
st.header("Executive Summary")

st.write(f"""
- Total Users: {total_users}
- Conversion Rate: {conversion_rate}%
- Highest Drop-off Stage: {max_stage}
- Key focus should be improving conversion at critical stages and optimizing user experience
""")
