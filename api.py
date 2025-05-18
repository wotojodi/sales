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


# ----------------- CONFIG -----------------
st.set_page_config(page_title="Sales and Marketing Dashboard", layout="wide", initial_sidebar_state="collapsed")

# ----------------- AUTO REFRESH -----------------
st_autorefresh(interval=60, key="auto_refresh")

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
@st.cache_data
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
if selected == "Sales":
    st.title("📈 Sales Performance Dashboard")

    # --- KPIs: Quick Glance at Sales Health ---
    st.markdown("###  Key Performance Indicators")
    total_customers = filtered_df["Customer ID"].count()
    total_countries = filtered_df["Country"].nunique()
    total_sales_revenue = filtered_df[filtered_df["Product Status"] == "Completed"]["Sales Amount"].sum()
    total_profit = filtered_df['Profit'].sum()
    total_loss = filtered_df['Loss'].sum()
    total_job_request = filtered_df["Product Type"].count()
    subscribers = filtered_df[filtered_df["Subscription Type"].isin(["Premium", "Standard"])].shape[0]
    subscriptions_price = filtered_df[filtered_df["Subscription Type"] != "Free"]["Subscription Price"].sum()
    AI_assistant = filtered_df[filtered_df["Assistance Type"] == 'AI-powered virtual assistant'].shape[0]
    sales_rep = filtered_df[filtered_df["Assistance Type"] == 'Sales Representative'].shape[0]
    top_selling = filtered_df["Product Type"].value_counts().idxmax()

    kpi_row1 = st.columns(3)
    kpi_row1[0].metric(label=" Total Sales Revenue", value=f"${total_sales_revenue:,.2f}")
    kpi_row1[1].metric(label=" Total Profit", value=f"${total_profit:,.2f}")
    kpi_row1[2].metric(label="Total Loss", value=f"${total_loss:,.2f}")

    kpi_row2 = st.columns(3)
    kpi_row2[0].metric(label=" Total Customers", value=total_customers)
    kpi_row2[1].metric(label=" Countries Reached", value=total_countries)
    kpi_row2[2].metric(label=" Total Job Requests", value=total_job_request)

    kpi_row3 = st.columns(3)
    kpi_row3[0].metric(label=" AI Assistant Requests", value=AI_assistant)
    kpi_row3[1].metric(label="Sales Rep Requests", value=sales_rep)
    kpi_row3[2].metric(label="Top Selling Product", value=top_selling)

    kpi_row4 = st.columns(2)
    kpi_row4[0].metric(label=" Total Subscribers", value=subscribers)
    kpi_row4[1].metric(label=" Subscription Revenue", value=f"${subscriptions_price:,.2f}")

    # --- Revenue Over Time ---
    with st.expander("📅 Revenue Trends Over Time", expanded=False):
        completed_df = filtered_df[filtered_df['Product Status'] == 'Completed'].copy()
        completed_df['Month'] = pd.to_datetime(completed_df['Sales Date']).dt.month_name()

        fig2 = px.bar(
            completed_df.groupby('Month')['Sales Amount'].sum()
            .reindex([
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]).reset_index(),
            x='Month',
            y='Sales Amount',
            title=' Monthly Sales Revenue'
        )

        st.plotly_chart(fig2, use_container_width=True)


    # --- Product-Level Performance ---
    with st.expander("🏷️ Product Sales Insights", expanded=False):
        # Ensure you're using only completed sales for meaningful sales metrics
        completed_df = filtered_df[filtered_df['Product Status'] == 'Completed']

        # Extract Top & Least Selling Products
        def get_top_least_products(data):
            product_sales = data.groupby("Product Type")["Sales Amount"].sum().reset_index()
            product_sales = product_sales.sort_values(by="Sales Amount", ascending=False)
            top_10 = product_sales.head(10)
            return top_10

        top_products, least_products = get_top_least_products(completed_df)

        fig_top = px.bar(
            top_products,
            x='Product Type',
            y='Sales Amount',
            title=' Top 10 Best-Selling Products',
        )
        fig_top.update_layout(xaxis_tickangle=-45)


        filtered_df = df.sort_values(by='Loss', ascending=False)  # no .head()

        fig_loss = px.bar(
            filtered_df,
            x='Product Type',
            y='Loss',
            title=' Loss by Product Type'
        )

        st.plotly_chart(fig_top, use_container_width=True)
        st.plotly_chart(fig_loss, use_container_width=True)


    # --- Country-Level Performance ---
    with st.expander("🌐 Country-Level Sales Breakdown", expanded=False):
        top_countries = completed_df.groupby('Country')['Sales Amount'].sum().sort_values(ascending=False).head(10).reset_index()

        fig_top_countries = px.bar(
            top_countries,
            x='Country',
            y='Sales Amount',
            title=' Top 10 Countries by Sales Revenue',
            color='Sales Amount'
        )

        st.plotly_chart(fig_top_countries, use_container_width=True)

    # --- Subscription Sales Breakdown ---
    with st.expander(" Subscription-Based Revenue Analysis", expanded=False):
        fig_col1, fig_col2 = st.columns(2)

        with fig_col1:
            subscription_price_by_type = filtered_df.groupby('Subscription Type')['Subscription Price'].sum().reset_index()
            fig_subs = px.pie(
                subscription_price_by_type,
                names='Subscription Type',
                values='Subscription Price',
                title=' Revenue Distribution by Subscription Type'
            )
            st.plotly_chart(fig_subs, use_container_width=True)

        with fig_col2:
            fig_customer_type = px.histogram(
                filtered_df,
                x='Customer Type',
                y='Sales Amount',
                title=' Customer Type vs Sales Amount'
            )
            st.plotly_chart(fig_customer_type, use_container_width=True)

    
        
# ----------------- EFFECTIVENESS TAB -----------------
elif selected == "Effectiveness":
    st.subheader("Effectiveness Analysis")
    # Calculate stars out of 5
    def get_star_rating(rating):
        full_stars = int(rating)
        half_star = rating - full_stars >= 0.5
        stars = "⭐" * full_stars
        if half_star:
            stars += "✬"
        return stars

    avg_rating = filtered_df['Product Rating'].mean()
    stars = get_star_rating(avg_rating)
    refund_rate = filtered_df['Refund Amount'].sum()
    avg_response_time = filtered_df['Response Time (days)'].mean()
    demo = filtered_df[filtered_df["Demo Scheduled"] == 'Yes'].shape[0]
    total_promotion= filtered_df[filtered_df["Promotional Event Participation"]== 'Yes'].shape[0]
    completed = filtered_df[filtered_df['Product Status'] == 'Completed']
    conversion_rate = round((len(completed) / demo) * 100, 2) if demo > 0 else 0


    with st.expander("📌 Effectiveness KPIs", expanded=True):
        kpis_row1 = st.columns(3)
        kpis_row2 = st.columns(3)
        
        kpis_row1[0].metric("Avg. Product Rating", f"{avg_rating:.2f}  {stars}")
        kpis_row1[1].metric("Avg. Response Time (days)", f"{avg_response_time:.2f}")
        kpis_row1[2].metric("Refund Amount", f"{refund_rate:.2f}")
        
        kpis_row2[0].metric("Sheduled demos", value=demo)
        kpis_row2[1].metric("Event Participation", value=total_promotion)
        kpis_row2[2].metric("Conversion rate", value=conversion_rate)

    # --- Product Ratings ---
    with st.expander("⭐ Ratings by Product Performance", expanded=False):
        top_selling = filtered_df["Product Type"].value_counts().nlargest(5).index
        least_selling = filtered_df["Product Type"].value_counts().nsmallest(5).index

        fig_top = px.box(
            filtered_df[filtered_df["Product Type"].isin(top_selling)],
            x="Product Type", y="Product Rating",
            title="Top-Selling Products: Rating Distribution"
        )
        st.plotly_chart(fig_top, use_container_width=True)


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
            x="Response Time (days)", nbins=10,
            title="Distribution of Product Completion Times"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # --- Product Status ---
    with st.expander("📦 Product Status Overview", expanded=False):
        status_counts = filtered_df['Product Status'].value_counts().reset_index()
        status_counts.columns = ['Product Status', 'Count']
        fig_status = px.bar(
            status_counts,
            x='Product Status', y='Count', color='Product Status',
            title='Product Status Distribution', text='Count'
        )
        st.plotly_chart(fig_status, use_container_width=True)

    
# ----------------- ANALYSIS TAB -----------------
elif selected == "Analysis":
    st.subheader("🧾 Deeper Data Analysis")

    # Combined Aggregated Table by Country and Product Type
    with st.expander("🌍 Combined Summary: Country vs Product Type", expanded=True):
        st.write("This table combines country and product type performance across key financial and satisfaction metrics.")

        combined_summary = (
            filtered_df.groupby(["Country", "Product Type"])[
                ["Sales Amount", "Cost of Product", "Profit", "Loss", "Response Time (days)", "Product Rating"]
            ]
            .agg(['sum', 'mean', 'count'])
            .round(2)
        )

        # Sort by highest total sales
        combined_summary = combined_summary.sort_values(('Sales Amount', 'sum'), ascending=False)
        
        st.dataframe(combined_summary, use_container_width=True)
    # Ensure Date column is datetime
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])

    # Create time features
    filtered_df["Day"] = filtered_df["Date"].dt.date
    filtered_df["Month"] = filtered_df["Date"].dt.to_period("M").astype(str)
    filtered_df["Year"] = filtered_df["Date"].dt.year

    with st.expander("📈 Time-Based Profit & Loss Summary", expanded=True):
        st.write("This section shows daily, monthly, and yearly trends of profit and loss.")

        # Daily
        daily = filtered_df.groupby("Day")[["Profit", "Loss"]].sum().round(2)
        st.markdown("#### 📆 Daily Profit & Loss")
        st.dataframe(daily.tail(30), use_container_width=True)  # show last 30 days

        # Monthly
        monthly = filtered_df.groupby("Month")[["Profit", "Loss"]].sum().round(2)
        st.markdown("#### 🗓️ Monthly Profit & Loss")
        st.dataframe(monthly.tail(12), use_container_width=True)

        # Yearly
        yearly = filtered_df.groupby("Year")[["Profit", "Loss"]].sum().round(2)
        st.markdown("#### 📅 Yearly Profit & Loss")
        st.dataframe(yearly, use_container_width=True)


    # Descriptive Statistics Summary
    with st.expander("📌 Descriptive Statistics Overview", expanded=False):
        st.write("This section provides a statistical overview of key numerical metrics in the dataset, including counts, means, and standard deviations.")
        st.dataframe(filtered_df.describe().round(2), use_container_width=True)

