# login_dashboard.py

import streamlit as st
import time
import json
import os
import pandas as pd
import plotly.express as px
from io import BytesIO
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
from Generating_data import create_record
import numpy as np


# ----------------- CONFIG -----------------
st.set_page_config(page_title="Sales and Marketing Dashboard", layout="wide")

# ----------------- AUTO REFRESH -----------------
st_autorefresh(interval=60000, limit=None, key="data_refresh")

# 1. Append ne# 1. Append new record
CSV_PATH = 'AI_Solution_Dataset.csv'
new_record = create_record()
new_df = pd.DataFrame([new_record])

# Ensure the file exists and is correctly written before reading
if not os.path.exists(CSV_PATH):
    new_df.to_csv(CSV_PATH, index=False)
else:
    with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        new_df.to_csv(f, header=False, index=False)

# 2. Load data only once after writing
def load_data():
    try:
        df = pd.read_csv(CSV_PATH, on_bad_lines='skip')
        df.columns = df.columns.str.strip()  # Clean column names
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

df = load_data()

# ----------------- SIDEBAR FILTERS -----------------
st.sidebar.header("Filter Options")
country_filter = st.sidebar.multiselect("Select Country", options=df['Country'].unique())
product_filter = st.sidebar.multiselect("Select Product", options=df['Product Type'].unique())
year_filter = st.sidebar.multiselect("Select Year", options=df['Sales Date'].astype(str).str[:4].unique())

filtered_df = df.copy()
if country_filter:
    filtered_df = filtered_df[filtered_df['Country'].isin(country_filter)]
if product_filter:
    filtered_df = filtered_df[filtered_df['Product Type'].isin(product_filter)]
if year_filter:
    filtered_df = filtered_df[filtered_df['Sales Date'].astype(str).str[:4].isin(year_filter)]

# ----------------- NAVIGATION MENU -----------------
selected = option_menu(
    menu_title=None,
    options=["Sales", "Effectiveness", "Analysis"],
    icons=[],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"},
        "nav-link": {"font-size": "25px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "green"},
    }
)

# ----------------- EXPORT CSV -----------------
st.subheader("Export Filtered Data")
towrite = BytesIO()
filtered_df.to_csv(towrite, index=False)
towrite.seek(0)
st.download_button("Export to CSV", data=towrite, file_name="Filtered_AI_Data.csv", mime="text/csv")
#-------------------- tabs-----------------

# --- SALES TAB ---
if selected == "Sales":
    st.title("📈 Sales Performance Dashboard")

    # --- KPIs: Quick Glance at Sales Health ---
    st.markdown("### Key Performance Indicators")

    total_customers = filtered_df["Customer ID"].nunique()
    total_countries = filtered_df["Country"].nunique()
    completed_sales = filtered_df[filtered_df["Product Status"] == "Completed"]
    total_sales_revenue = completed_sales["Sales Amount"].sum()
    total_profit = filtered_df['Profit'].sum()
    total_loss = filtered_df['Loss'].sum()
    total_job_request = filtered_df["Product Type"].count()
    subscribers = filtered_df[filtered_df["Subscription Type"].isin(["Premium", "Standard"])].shape[0]
    subscriptions_price = filtered_df[filtered_df["Subscription Type"] != "Free"]["Subscription Price"].sum()
    AI_assistant = filtered_df[filtered_df["Assistance Type"] == 'AI-powered virtual assistant'].shape[0]
    sales_rep = filtered_df[filtered_df["Assistance Type"] == 'Sales Representative'].shape[0]
    top_selling = filtered_df["Product Type"].value_counts().idxmax()

    benchmark_sales = 1000000  # example benchmark values for context
    benchmark_profit = 200000
    benchmark_customers = 5000

    kpi_row1 = st.columns(3)
    kpi_row1[0].metric("Total Sales Revenue", f"${total_sales_revenue:,.2f}", delta=f"${total_sales_revenue - benchmark_sales:,.2f}")
    kpi_row1[1].metric("Total Profit", f"${total_profit:,.2f}", delta=f"${total_profit - benchmark_profit:,.2f}")
    kpi_row1[2].metric("Total Loss", f"${total_loss:,.2f}")

    kpi_row2 = st.columns(3)
    kpi_row2[0].metric("Total Customers", total_customers, delta=f"{total_customers - benchmark_customers}")
    kpi_row2[1].metric("Countries Reached", total_countries)
    kpi_row2[2].metric("Total Job Requests", total_job_request)

    kpi_row3 = st.columns(3)
    kpi_row3[0].metric("AI Assistant Requests", AI_assistant)
    kpi_row3[1].metric("Sales Rep Requests", sales_rep)
    kpi_row3[2].metric("Top Selling Product", top_selling)

    kpi_row4 = st.columns(2)
    kpi_row4[0].metric("Total Subscribers", subscribers)
    kpi_row4[1].metric("Subscription Revenue", f"${subscriptions_price:,.2f}")

    # --- Revenue Over Time ---
    with st.expander("📅 Revenue Trends Over Time", expanded=False):
        completed_df = completed_sales.copy()
        completed_df['Sales Date'] = pd.to_datetime(completed_df['Sales Date'], errors='coerce')
        completed_df['Month'] = completed_df['Sales Date'].dt.to_period('M').dt.to_timestamp()

        monthly_sales = completed_df.groupby('Month')['Sales Amount'].sum().reset_index()
        fig = px.line(monthly_sales, x='Month', y='Sales Amount', title='Monthly Sales Revenue')
        st.plotly_chart(fig, use_container_width=True)

        # Sales forecast for next 3 months using simple linear extrapolation
        if len(monthly_sales) > 3:
            recent = monthly_sales.tail(3)
            x = np.arange(len(recent))
            y = recent['Sales Amount'].values
            coeffs = np.polyfit(x, y, 1)
            forecast_x = np.arange(len(recent), len(recent)+3)
            forecast_y = coeffs[0]*forecast_x + coeffs[1]
            forecast_months = pd.date_range(start=monthly_sales['Month'].max()+pd.offsets.MonthBegin(), periods=3, freq='MS')
            forecast_df = pd.DataFrame({"Month": forecast_months, "Forecasted Sales": forecast_y})
            fig2 = px.line(forecast_df, x='Month', y='Forecasted Sales', title='3-Month Sales Forecast')
            st.plotly_chart(fig2, use_container_width=True)

    # --- Sales Trend Heatmap by Month and Product ---
    with st.expander("📊 Sales Trend Heatmap by Month and Product", expanded=False):
        heatmap_df = completed_df.groupby(['Month', 'Product Type'])['Sales Amount'].sum().reset_index()
        heatmap_pivot = heatmap_df.pivot(index='Product Type', columns='Month', values='Sales Amount').fillna(0)
        fig_heatmap = px.imshow(
            heatmap_pivot,
            labels=dict(x="Month", y="Product Type", color="Sales Amount"),
            title="Sales Heatmap (Product vs. Month)"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

# --- EFFECTIVENESS TAB ---
elif selected == "Effectiveness":
    st.subheader("Effectiveness Analysis")

    def get_star_rating(rating):
        full_stars = int(rating)
        half_star = rating - full_stars >= 0.5
        stars = "⭐" * full_stars
        if half_star:
            stars += "✬"
        return stars

    filtered_df['Product Rating'] = pd.to_numeric(filtered_df['Product Rating'], errors='coerce').fillna(0)
    avg_rating = filtered_df['Product Rating'].mean()
    stars = get_star_rating(avg_rating)
    refund_rate = filtered_df['Refund Amount'].sum()
    avg_response_time = filtered_df['Response Time (days)'].mean()
    demo = filtered_df[filtered_df["Demo Scheduled"] == 'Yes'].shape[0]
    total_promotion = filtered_df[filtered_df["Promotional Event Participation"] == 'Yes'].shape[0]
    completed = filtered_df[filtered_df['Product Status'] == 'Completed']
    conversion_rate = round((len(completed) / demo) * 100, 2) if demo > 0 else 0

    # Benchmarks or context values for KPIs for comparison
    benchmark_rating = 4.0
    benchmark_response = 3.0
    benchmark_refund = 5000

    with st.expander("📌 Effectiveness KPIs", expanded=True):
        kpis_row1 = st.columns(3)
        kpis_row2 = st.columns(3)

        kpis_row1[0].metric("Avg. Product Rating", f"{avg_rating:.2f}  {stars}", delta=f"{avg_rating - benchmark_rating:.2f}")
        kpis_row1[1].metric("Avg. Response Time (days)", f"{avg_response_time:.2f}", delta=f"{avg_response_time - benchmark_response:.2f}")
        kpis_row1[2].metric("Total Refund Amount", f"${refund_rate:,.2f}", delta=f"${refund_rate - benchmark_refund:,.2f}")

        kpis_row2[0].metric("Scheduled Demos", value=demo)
        kpis_row2[1].metric("Event Participation", value=total_promotion)
        kpis_row2[2].metric("Conversion Rate (%)", value=conversion_rate)

    # --- Product Ratings Distribution ---
    with st.expander("⭐ Ratings by Product Performance", expanded=False):
        top_selling = filtered_df["Product Type"].value_counts().nlargest(5).index

        fig_box = px.box(
            filtered_df[filtered_df["Product Type"].isin(top_selling)],
            x="Product Type", y="Product Rating",
            title="Top-Selling Products: Rating Distribution"
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # --- Refund Distribution ---
    with st.expander("💸 Refund Analysis by Product", expanded=False):
        fig_refund = px.box(
            filtered_df[filtered_df["Refund Amount"] > 0],
            x="Product Type", y="Refund Amount",
            title="Refund Distribution by Product Type"
        )
        st.plotly_chart(fig_refund, use_container_width=True)

    # --- Response Time Distribution ---
    with st.expander("⏱️ Response Time Analysis", expanded=False):
        fig_hist = px.histogram(
            filtered_df,
            x="Response Time (days)", nbins=20,
            title="Distribution of Product Completion Times"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # --- Customer Comments Sentiment (basic keywords) ---
    with st.expander("💬 Customer Comments Sentiment", expanded=False):
        positive_keywords = ['Excellent', 'Great', 'Loved', 'Fantastic', 'Highly recommend', 'Will buy again']
        negative_keywords = ['Cancel', 'delay', 'not as described', 'poor']

        comments = filtered_df['Comments'].dropna().astype(str)

        pos_count = comments.apply(lambda x: any(word.lower() in x.lower() for word in positive_keywords)).sum()
        neg_count = comments.apply(lambda x: any(word.lower() in x.lower() for word in negative_keywords)).sum()
        neutral_count = len(comments) - pos_count - neg_count

        sentiments = pd.DataFrame({
            'Sentiment': ['Positive', 'Negative', 'Neutral'],
            'Count': [pos_count, neg_count, neutral_count]
        })

        fig_sentiment = px.pie(sentiments, values='Count', names='Sentiment', title='Customer Sentiment Distribution')
        st.plotly_chart(fig_sentiment, use_container_width=True)
