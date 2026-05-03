import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Funnel Analytics Dashboard", layout="wide")

st.title("Customer Funnel Analytics Dashboard")
st.markdown("Analysis of user progression, conversion, and drop-offs across funnel stages")

# ----------------------------
# LOAD DATA
# ----------------------------
uploaded_file = st.sidebar.file_uploader("Upload Dataset (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("final_forex_dataset.csv")

# ----------------------------
# RENAME COLUMNS FOR CLARITY
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

def create_filter(column_name):
    values = sorted(df[column_name].dropna().unique())
    return st.sidebar.multiselect(column_name, values, default=values)

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

# Maintain logical order
stage_order = ["Initiated", "KYC Completed", "Completed"]
if set(stage_order).issubset(set(funnel["Stage"])):
    funnel["Stage"] = pd.Categorical(funnel["Stage"], categories=stage_order, ordered=True)

funnel = funnel.sort_values("Stage").reset_index(drop=True)

# Enforce monotonic funnel
funnel["User ID"] = funnel["User ID"].cummin()

# Metrics
base_users = funnel.iloc[0]["User ID"]

funnel["Conversion (%)"] = (funnel["User ID"] / base_users) * 100
funnel["Drop-Off"] = funnel["User ID"].shift(1) - funnel["User ID"]
funnel["Drop-Off (%)"] = (funnel["Drop-Off"] / funnel["User ID"].shift(1)) * 100

funnel = funnel.fillna(0)

# ----------------------------
# KPI SECTION
# ----------------------------
total_users = base_users
completed_users = funnel.iloc[-1]["User ID"]
conversion_rate = round((completed_users / total_users) * 100, 2)

col1, col2, col3 = st.columns(3)
col1.metric("Total Users", total_users)
col2.metric("Completed Transactions", completed_users)
col3.metric("Conversion Rate (%)", conversion_rate)

# ----------------------------
# FUNNEL VISUAL
# ----------------------------
st.subheader("Funnel Overview")

fig = px.funnel(
    funnel,
    x="User ID",
    y="Stage"
)
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# FUNNEL TABLE
# ----------------------------
st.subheader("Stage-wise Metrics")

st.dataframe(funnel.style.format({
    "Conversion (%)": "{:.2f}",
    "Drop-Off (%)": "{:.2f}"
}))

# ----------------------------
# INSIGHTS
# ----------------------------
st.subheader("Key Insights")

max_drop_idx = funnel["Drop-Off (%)"].idxmax()
max_drop_stage = funnel.loc[max_drop_idx, "Stage"]
max_drop_value = funnel.loc[max_drop_idx, "Drop-Off (%)"]

st.write(f"Highest drop-off occurs at **{max_drop_stage}** with a drop of **{round(max_drop_value,2)}%**.")

if max_drop_value > 50:
    st.write("Significant friction detected at this stage. Immediate intervention may be required.")
elif max_drop_value > 30:
    st.write("Moderate drop-off observed. Optimization opportunities exist.")
else:
    st.write("Funnel performance appears stable across stages.")

# ----------------------------
# REVENUE IMPACT
# ----------------------------
if "Transaction Amount" in filtered_df.columns:
    avg_value = filtered_df["Transaction Amount"].mean()
    total_drop_users = funnel["Drop-Off"].sum()
    revenue_loss = int(avg_value * total_drop_users)

    st.subheader("Estimated Revenue Impact")
    st.metric("Potential Revenue Loss", f"{revenue_loss:,}")

# ----------------------------
# CUSTOMER SEGMENT ANALYSIS
# ----------------------------
if "Customer Type" in filtered_df.columns:
    st.subheader("Customer Segment Performance")

    seg = filtered_df.groupby(["Customer Type", "Stage"])["User ID"].nunique().reset_index()

    fig2 = px.line(
        seg,
        x="Stage",
        y="User ID",
        color="Customer Type",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# CHANNEL ANALYSIS
# ----------------------------
if "Channel" in filtered_df.columns:
    st.subheader("Channel-wise Performance")

    ch = filtered_df.groupby(["Channel", "Stage"])["User ID"].nunique().reset_index()

    fig3 = px.bar(
        ch,
        x="Stage",
        y="User ID",
        color="Channel",
        barmode="group"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ----------------------------
# PROCESSING TIME ANALYSIS
# ----------------------------
if "Processing Time (mins)" in filtered_df.columns:
    st.subheader("Processing Time by Stage")

    tat = filtered_df.groupby("Stage")["Processing Time (mins)"].mean().reset_index()

    fig4 = px.bar(
        tat,
        x="Stage",
        y="Processing Time (mins)"
    )
    st.plotly_chart(fig4, use_container_width=True)

# ----------------------------
# FINAL TAKEAWAYS
# ----------------------------
st.subheader("Summary")

st.write(f"""
- Maximum drop-off occurs at **{max_drop_stage}**
- Overall conversion rate stands at **{conversion_rate}%**
- Key focus should be on improving performance at critical funnel stages
- Segment and channel analysis can guide targeted interventions
""")
