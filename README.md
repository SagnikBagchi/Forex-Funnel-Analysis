# Forex-Funnel-Analysis
Customer Funnel Analytics Dashboard
Overview

This project is an interactive Customer Funnel Analytics Dashboard built using Streamlit. It analyzes user behavior across a multi-stage funnel to identify drop-offs, conversion patterns, and business impact.

The primary objective is to transform raw behavioral data into actionable product and business insights, similar to what is done in real-world product analytics teams.

Problem Statement

In most digital products, users drop off at different stages of their journey. However, understanding:

Where users drop off
Why they drop off
Which segments perform better
Which channels drive higher conversions

is often difficult using raw data alone.

This project addresses that gap by building a structured funnel analytics system that helps simulate real-world product decision-making.

Dataset Used

This project uses the Ecommerce Behavior Dataset from Multi Category Store:

https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store

Why this dataset?

The dataset contains large-scale user behavior data including:

Product views
Cart interactions
Purchases

Since real-world financial funnel data is not publicly available, this dataset was adapted to simulate a financial product journey.

Funnel Mapping Logic

To convert ecommerce behavior into a business funnel model, the following mapping was used:

Ecommerce Event	Funnel Stage
view	Initiated
cart	KYC Stage
purchase	Completed

This allows simulation of a real-world onboarding + conversion funnel similar to financial or fintech products.

Feature Engineering

To enhance analytical depth, additional features were engineered:

Customer Type → New vs Repeat users
Channel → Mobile / Web / Branch (simulated)
Transaction Amount → Revenue impact analysis
Processing Time (TAT) → Operational efficiency metric

These features enable multi-dimensional analysis of user behavior.

Key Features of the Dashboard

1. Funnel Analysis
Stage-wise user progression
Conversion percentage calculation
Drop-off identification
2. Segmentation Analysis
Comparison of new vs repeat users
Behavior differences across customer types
3. Channel Performance
Conversion comparison across platforms (Mobile, Web, Branch)
Identification of high and low-performing channels
4. Transaction Value Analysis
Distribution of transaction amounts across stages
Identification of high-value drop-offs
5. Operational Efficiency
Processing time vs conversion relationship
Impact of delays on user drop-off
6. Business Impact Estimation
Estimated revenue loss due to funnel drop-offs
Value conversion rate calculation
📈 Key Insights
Significant drop-offs occur at mid-funnel stages (KYC equivalent stage)
Repeat users consistently outperform new users in conversion
Channel behavior varies significantly, indicating UX differences
Higher processing time is correlated with lower conversion rates
Funnel leakage can be translated into measurable revenue impact

Business Impact

This project demonstrates how raw behavioral data can be transformed into:

Product optimization insights
User experience improvements
Revenue impact estimation
Operational efficiency analysis

It reflects real-world Product Analytics / Business Analytics use cases.

Tech Stack

Python
Pandas
Streamlit
Plotly
