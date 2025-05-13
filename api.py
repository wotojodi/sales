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
COOKIE_FILE = "session_cookie.json"
SESSION_DURATION = 3600  # 1 hour
VALID_USERNAME = "kwoto"
VALID_PASSWORD = "abc"

# ----------------- SESSION HANDLING -----------------
def load_cookie():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "r") as f:
            cookie = json.load(f)
            if cookie.get("expiry_time", 0) > time.time():
                return True
    return False

def save_cookie():
    with open(COOKIE_FILE, "w") as f:
        cookie = {
            "authenticated": True,
            "expiry_time": time.time() + SESSION_DURATION
        }
        json.dump(cookie, f)

def clear_cookie():
    if os.path.exists(COOKIE_FILE):
        os.remove(COOKIE_FILE)

# ----------------- LOGIN FORM -----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = load_cookie()

if not st.session_state.authenticated:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.authenticated = True
            save_cookie()
            st.success("Login successful! Refreshing...")
            st.rerun()
        else:
            st.error("Invalid credentials.")
    st.stop()

# ----------------- AUTO REFRESH -----------------
st_autorefresh(interval=10, key="auto_refresh")

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
try:
    df = pd.read_csv(CSV_PATH, on_bad_lines='skip')
    df.columns = df.columns.str.strip()  # Clean column names
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()




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
    options=["Sales", "Effectiveness", "Analysis", "Logout"],
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

# ----------------- TABS -----------------
if selected == "Sales":
    st.title("Sales Overview")
    total_customers= filtered_df["Customer ID"].count()
    total_countries=filtered_df["Country"].count()
    total_sales_revenue = filtered_df[filtered_df["Product Status"] == "Completed"]["Sales Amount"].sum()
    total_profit = filtered_df['Profit'].sum()
    total_loss = filtered_df['Loss'].sum()
    total_job_request = filtered_df["Product Type"].count()
    subscribers = filtered_df[filtered_df["Subscription Type"].isin(["Premium", "Standard"])].shape[0]
    subscriptions_price=filtered_df[filtered_df["Subscription Type"] != "Free"]["Subscription Price"].sum()
    demo = filtered_df[filtered_df["Demo Scheduled"] == 'Yes'].shape[0]
    total_promotion= filtered_df[filtered_df["Promotional Event Participation"]== 'Yes'].shape[0]
    AI_assistant = filtered_df[filtered_df["Assistance Type"] == 'AI-powered virtual assistant'].shape[0]
    top_selling=filtered_df["Product Type"].value_counts().idxmax()
    sales_rep=filtered_df[filtered_df["Assistance Type"] == 'Sales Representative'].shape[0]

    with st.expander("📊 Key Performance Indicators", expanded=True):
        kpi_row1 = st.columns(3)
        kpi_row2 = st.columns(3)
        kpi_row3 = st.columns(3)
        kpi_row4 = st.columns(3)
        

       # Row 1 – Financial Outcomes (Most Important KPIs First)
        kpi_row1[0].metric(label="Total Sales Revenue", value=f"${total_sales_revenue:,.2f}") 
        kpi_row1[1].metric(label="Total Profit", value=f"${total_profit:,.2f}")
        kpi_row1[2].metric(label="Total Loss", value=f"${total_loss:,.2f}")

        # Row 2 – Sales Performance & Conversion
        kpi_row2[0].metric(label="Top Selling Product", value=top_selling)
        kpi_row2[1].metric(label="Total number of Subscriptions", value=subscribers)
        kpi_row2[2].metric(label="Subscription Revenue", value=subscriptions_price)

        # Row 3 – Customer Reach & Engagement
        kpi_row3[0].metric(label="Total Customers", value=total_customers)
        kpi_row3[1].metric(label="Total number of Countries", value=total_countries)
        kpi_row3[2].metric(label="Total Job Request", value=total_job_request)

        # Row 4 – Support & Sales Channels
        kpi_row4[0].metric(label="Request for Sales Rep", value=sales_rep)
        kpi_row4[1].metric(label="Request for AI-powered virtual assistant", value=AI_assistant)
        kpi_row4[2].metric(label="Promo Event Participation", value=total_promotion)

    # Section 1: Overall Financial Performance
    with st.expander("💰 Financial Performance", expanded=False):
        fig_col1, fig_col2, fig_col3 = st.columns(3)

        with fig_col1:
            @st.cache_data(ttl=60)
            completed_df = filtered_df[filtered_df['Product Status'] == 'Completed']
            fig1 = px.bar(
                completed_df.groupby('Sales Date').sum().reset_index(),
                x='Sales Date', 
                y='Sales Amount', 
                title='Yearly Sales Revenue'
            )
            st.plotly_chart(fig1, use_container_width=True, dynamic=False)

        with fig_col2:
            @st.cache_data(ttl=60)
            def get_top_least_products(data):
                product_sales = data.groupby("Product Type")["Sales Amount"].sum().reset_index()
                product_sales = product_sales.sort_values(by="Sales Amount", ascending=False)
                top_10 = product_sales.head(10)
                least_10 = product_sales.tail(10)
                return top_10, least_10
        
            top_products, least_products = get_top_least_products(completed_df)
            fig_top = px.bar(
                top_products,
                x='Product Type',
                y='Sales Amount',
                title='Top 10 Best-Selling Products',
                text_auto='.2s'
            )
            fig_top.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_top, use_container_width=True, dynamic=False)
        with fig_col3:
            @st.cache_data(ttl=60)
            fig_least = px.bar(
                least_products,
                x='Product Type',
                y='Sales Amount',
                title='Least 10 Selling Products',
                text_auto='.2s'
            )
            fig_least.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_least, use_container_width=True, dynamic=False)
        
        fig_co1, fig_co2, fig_co3 = st.columns(3)

        with fig_co1:
            @st.cache_data(ttl=60)
            fig3 = px.bar(
                filtered_df, 
                x='Product Type', 
                y='Loss', 
                title='Loss by Product Type'
            )
        
            st.plotly_chart(fig3, use_container_width=True, dynamic=False)
        
        with fig_co2:   
            @st.cache_data(ttl=60)
            # Layout for wide choropleth map
            st.subheader("Sales Revenue by Country")
            fig_map = px.choropleth(
                completed_df,
                locations='Country',
                locationmode='country names',
                color='Sales Amount',
                title='Choropleth Map: Sales Revenue by Country',
                color_continuous_scale=px.colors.sequential.Plasma
            )
            st.plotly_chart(fig_map, use_container_width=True, dynamic=False)

    # Section 2: Subscription Insights
    with st.expander("📦 Subscription Insights", expanded=False):
        fig_col4, fig_col5, fig_col6 = st.columns(3)

        with fig_col4:
            @st.cache_data(ttl=60)
            subscription_price_by_type = filtered_df.groupby('Subscription Type')['Subscription Price'].sum().reset_index()
            fig4 = px.pie(
                subscription_price_by_type,
                names='Subscription Type',
                values='Subscription Price',
                title='Revenue by Subscription Type'
            )
            st.plotly_chart(fig4, use_container_width=True, dynamic=False)

        with fig_col5:
            @st.cache_data(ttl=60)
            fig5 = px.histogram(filtered_df, 
                x='Customer Type', 
                y='Sales Amount', 
                title='Customer Type vs Sales Amount'
            )
            st.plotly_chart(fig5, use_container_width=True, dynamic=False)

    
        

    
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
    completed_product = filtered_df[filtered_df["Product Status"] == "Completed"].shape[0]
    canceled_product = filtered_df[filtered_df["Product Status"] == "Canceled"].shape[0]
    failed_product = filtered_df[filtered_df["Product Status"] == "Failed"].shape[0]

    with st.expander("📌 Effectiveness KPIs", expanded=True):
        kpis_row1 = st.columns(3)
        kpis_row2 = st.columns(3)
        
        kpis_row1[0].metric("Avg. Product Rating", f"{avg_rating:.2f}  {stars}")
        kpis_row1[1].metric("Refund Amount", f"{refund_rate:.2f}")
        kpis_row1[2].metric("Avg. Response Time (days)", f"{avg_response_time:.2f}")
        
        kpis_row2[0].metric("Completed Products", value=completed_product)
        kpis_row2[1].metric("Canceled Products", value=canceled_product)
        kpis_row2[2].metric("Failed Products", value=failed_product)

    with st.expander("📊 Customer Satisfaction & Ratings", expanded=False):
        @st.cache_data(ttl=60)
        rating_counts = filtered_df["Product Rating"].value_counts().sort_index()
        st.plotly_chart(px.bar(
            x=rating_counts.index,
            y=rating_counts.values,
            title="📈 Distribution of Product Ratings"
        ), use_container_width=True, dynamic=False)

        st.plotly_chart(px.box(
            filtered_df, x="Product Status", y="Product Rating",
            title="📦 Product Rating by Completion Status"
        ), use_container_width=True, dynamic=False)
    with st.expander("🪙 Rating by Subscription Tier", expanded=False):
        @st.cache_data(ttl=60)
        fig_sub_rating = px.box(
            filtered_df, x="Subscription Type", y="Product Rating",
            title="🔔 Rating by Subscription Type"
        )
        st.plotly_chart(fig_sub_rating, use_container_width=True, dynamic=False)
    with st.expander("📆 Customer Response Time", expanded=False):
        @st.cache_data(ttl=60)
        fig_response = px.histogram(
            filtered_df, x="Response Time (days)", nbins=10,
            title="⏱️ Distribution of Response Times"
        )
        st.plotly_chart(fig_response, use_container_width=True, dynamic=False)
    with st.expander("💸 Refund Analysis by Status", expanded=False):
        @st.cache_data(ttl=60)
        fig_refund = px.bar(
            filtered_df, x="Product Status", y="Refund Amount",
            title="Refund Amount by Product Status"
        )
        st.plotly_chart(fig_refund, use_container_width=True, dynamic=False)
    

# ----------------- ANALYSIS TAB -----------------
elif selected == "Analysis":
    st.subheader("Deeper Data Analysis")

    with st.expander("🧾 Aggregated Financial Overview by Country", expanded=True):
        st.write("This table summarizes the total, average, and number of records for Sales Amount, Profit, and Loss per country.")
        aggregated_data = (
            filtered_df.groupby("Country")[["Sales Amount", "Profit", "Loss"]]
            .agg(['sum', 'mean', 'count'])
            .round(2)
        )
        st.dataframe(aggregated_data, use_container_width=True)

    with st.expander("📌 Descriptive Statistics Summary", expanded=False):
        st.write("A statistical overview of the key numerical metrics in the dataset.")
        st.dataframe(filtered_df.describe().round(2), use_container_width=True)

    with st.expander("📋 Summary by Customer Type and Subscription", expanded=False):
        customer_summary = (
            filtered_df.groupby(["Customer Type", "Subscription Type"])[["Sales Amount", "Profit", "Loss"]]
            .agg(['sum', 'mean', 'count'])
            .round(2)
        )
        st.write("Sales, Profit, and Loss statistics broken down by customer type and subscription type.")
        st.dataframe(customer_summary, use_container_width=True)

    with st.expander("🕒 Response Time & Refund Insight Table", expanded=False):
        st.write("Examines how refund amounts relate to customer response times, broken down by product type.")
        response_refund = (
            filtered_df.groupby("Product Type")[["Response Time (days)", "Refund Amount"]]
            .agg(['mean', 'max', 'count'])
            .round(2)
        )
        st.dataframe(response_refund, use_container_width=True)
    with st.expander("Statistical Summary"):
        st.dataframe(filtered_df.describe())

elif selected == "Logout":
    clear_cookie()
    st.session_state.authenticated = False
    st.success("Logged out successfully. Please refresh.")
    st.stop()
