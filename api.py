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
CSV_PATH = 'AI_Solution_Dataset.csv'
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

# Auto-refresh every 2 seconds
st_autorefresh(interval=2000, key="auto_refresh")

# ----------------- FILE PATH -----------------
CSV_PATH = 'AI_Solution_Dataset.csv'

# ----------------- APPEND NEW DATA -----------------
if os.path.exists(CSV_PATH):
    new_record = create_record()
    new_df = pd.DataFrame([new_record])
    new_df.to_csv(CSV_PATH, mode='a', header=False, index=False)
else:
    initial_df = pd.DataFrame([create_record()])
    initial_df.to_csv(CSV_PATH, index=False)

# ----------------- READ UPDATED DATA -----------------
df = pd.read_csv(CSV_PATH, on_bad_lines="skip")

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

st.title("Sales and Marketing Dashboard")

# ----------------- COMMON FILTERS -----------------
st.sidebar.header("Filter Options")
country_filter = st.sidebar.multiselect("Select Country", options=df['Country'].unique())
product_filter = st.sidebar.multiselect("Select Product", options=df['Product Type'].unique())
year_filter = st.sidebar.multiselect("Select Year", options=df['Sales Date '].astype(str).str[:4].unique())

filtered_df = df.copy()
if country_filter:
    filtered_df = filtered_df[filtered_df['Country'].isin(country_filter)]
if product_filter:
    filtered_df = filtered_df[filtered_df['Product Type'].isin(product_filter)]
if year_filter:
    filtered_df = filtered_df[filtered_df['Sales Date '].astype(str).str[:4].isin(year_filter)]

# ----------------- EXPORT CSV -----------------
st.subheader("Export Filtered Data")
towrite = BytesIO()
filtered_df.to_csv(towrite, index=False)
towrite.seek(0)
st.download_button(
    label="Export to CSV",
    data=towrite,
    file_name='AI_Solution_Dataset.csv',
    mime='text/csv'
)

# ----------------- SALES TAB -----------------
if selected == "Sales":
    st.subheader("Sales Overview")

    total_sales_revenue = filtered_df['Sales Amount'].sum()
    average_sale_amount = filtered_df['Sales Amount'].mean()
    total_profit = filtered_df['Profit'].sum()
    total_loss = filtered_df['Loss'].sum()
    net_profit = total_profit - total_loss
    total_job_request = filtered_df["Product Type"].count()
    total_countries=filtered_df["Country"].count()
    subscriptions=filtered_df["Subscription Type"].count()
    subscriptions_price=filtered_df["Subscription Price"].sum()
    demo = filtered_df[filtered_df["Demo Scheduled"] == 'Yes'].shape[0]
    total_promotion= filtered_df[filtered_df["Promotional Event Participation"]== 'Yes'].shape[0]
    AI_assistant = filtered_df[filtered_df["Assistance Type"] == 'AI-powered virtual assistant'].shape[0]

    with st.expander("📊 Key Performance Indicators", expanded=True):
        kpi_row1 = st.columns(3)
        kpi_row2 = st.columns(3)
        kpi_row3 = st.columns(3)
        kpi_row4 = st.columns(3)


        kpi_row1[0].metric(label="Total Sales Revenue", value=f"${total_sales_revenue:,.2f}")
        kpi_row1[1].metric(label="Total Profit", value=f"${total_profit:,.2f}")
        kpi_row1[2].metric(label="Total Loss", value=f"${total_loss:,.2f}")

        kpi_row2[0].metric(label="Net Profit", value=f"${net_profit:,.2f}")
        kpi_row2[1].metric(label="Total Job Request", value=total_job_request)
        kpi_row2[2].metric(label="Average Sales Amount", value=f"{average_sale_amount:,.2f}")
        
        kpi_row3[0].metric(label="Total number of Countries",value=total_countries)
        kpi_row3[1].metric(label="Total number of Sbcriptions",value=subscriptions)
        kpi_row3[2].metric(label="Overall subscription amount",value=subscriptions_price)

        kpi_row4[0].metric(label="Total number of custmer who joined promotional events",value=total_promotion)
        kpi_row4[1].metric(label="Request for AI-powered virtual assistant",value=AI_assistant)

    with st.expander("📈 Sales & Profit Visualizations", expanded=False):
        fig_col1, fig_col2, fig_col3 = st.columns(3)

        with fig_col1:
            fig1 = px.bar(filtered_df, x=filtered_df['Sales Date '].astype(str).str[:4], y='Sales Amount', title='Sales over the Years')
            st.plotly_chart(fig1, use_container_width=True)

        with fig_col2:
            fig2 = px.choropleth(
                filtered_df, locations='Country', locationmode='country names',
                color='Sales Amount', title='Sales Revenue by Country',
                color_continuous_scale=px.colors.sequential.Plasma
            )
            st.plotly_chart(fig2, use_container_width=True)

        with fig_col3:
            fig3 = px.bar(filtered_df, x='Product Type', y='Profit', title='Profit by Product')
            st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📉 Loss & Subscriptions Visualizations", expanded=False):
        fig_col5, fig_col6, fig_col7 = st.columns(3)

        with fig_col5:
            fig5 = px.bar(filtered_df, x='Product Type', y='Loss', title="Loss by Product")
            st.plotly_chart(fig5, use_container_width=True)

        with fig_col6:
            fig6 = px.histogram(filtered_df, x='Customer Type', y='Sales Amount', title='Customer Type by Sales Amount')
            st.plotly_chart(fig6, use_container_width=True)

        with fig_col7:
            subscription_price_by_type = filtered_df.groupby('Subscription Type')['Subscription Price'].sum().reset_index()
            fig7 = px.pie(
                subscription_price_by_type,
                names='Subscription Type',
                values='Subscription Price',
                title='Total Subscription Price by Subscription Type'
            )
            st.plotly_chart(fig7, use_container_width=True)

# ----------------- EFFECTIVENESS TAB -----------------
if selected == "Effectiveness":
    st.subheader("Effectiveness Analysis")

    avg_rating = filtered_df['Product Rating'].mean()
    refund_rate = filtered_df['Refund Amount'].sum()
    avg_response_time = filtered_df['Response Time (days)'].mean()
    completed_product = filtered_df[filtered_df["Product Status"] == "Completed"].shape[0]
    canceled_product = filtered_df[filtered_df["Product Status"] == "Canceled"].shape[0]
    failed_product = filtered_df[filtered_df["Product Status"] == "Failed"].shape[0]

    with st.expander("📌 Effectiveness KPIs", expanded=True):
        kpis_row1 = st.columns(3)
        kpis_row2 = st.columns(3)
        
        kpis_row1[0].metric("Avg. Product Rating", f"{avg_rating:.2f}")
        kpis_row1[1].metric("Refund Amount", f"{refund_rate:.2f}")
        kpis_row1[2].metric("Avg. Response Time (days)", f"{avg_response_time:.2f}")
        
        kpis_row2[0].metric("Completed Products", value=completed_product)
        kpis_row2[1].metric("Canceled Products", value=canceled_product)
        kpis_row2[2].metric("Failed Products", value=failed_product)

    with st.expander("🎯 Product Rating Distribution", expanded=False):
        rating_counts = filtered_df["Product Rating"].value_counts().sort_index()
        fig_rating = px.bar(x=rating_counts.index, y=rating_counts.values, title="Distribution of Product Ratings")
        st.plotly_chart(fig_rating, use_container_width=True)

    with st.expander("🧠 Effectiveness by Product Status", expanded=False):
        fig_status_rating = px.box(filtered_df, x="Product Status", y="Product Rating", title="Product Rating by Status")
        st.plotly_chart(fig_status_rating, use_container_width=True)

    with st.expander("📍Product Status vs Refund Amount", expanded=False):
        fig_refund = px.bar(filtered_df, x="Product Status", y="Refund Amount", title="Refund Amount by Product Status")
        st.plotly_chart(fig_refund, use_container_width=True)

    with st.expander("📆 Response Time Effectiveness", expanded=False):
        fig_response = px.histogram(filtered_df, x="Response Time (days)", nbins=10, title="Distribution of Customer Response Times")
        st.plotly_chart(fig_response, use_container_width=True)

    with st.expander("📦 Rating by Subscription Type", expanded=False):
        fig_sub_rating = px.box(filtered_df, x="Subscription Type", y="Product Rating", title="Product Rating by Subscription Type")
        st.plotly_chart(fig_sub_rating, use_container_width=True)

    with st.expander("🌍 Avg Product Rating by Country", expanded=False):
        avg_rating_country = filtered_df.groupby("Country")["Product Rating"].mean().reset_index()
        fig_rating_country = px.bar(avg_rating_country.sort_values("Product Rating", ascending=False),
        x="Country", y="Product Rating", title="Average Product Rating by Country")
        st.plotly_chart(fig_rating_country, use_container_width=True)

    with st.expander("📉 Low Rated Product Types", expanded=False):
        low_rating_df = filtered_df[filtered_df["Product Rating"] <= 2]
        low_rating_count = low_rating_df["Product Type"].value_counts().reset_index()
        low_rating_count.columns = ["Product Type", "Low Rating Count"]
        fig_low_rating = px.bar(low_rating_count, x="Product Type", y="Low Rating Count",
        title="Low Ratings by Product Type")
        st.plotly_chart(fig_low_rating, use_container_width=True)

# ----------------- ANALYSIS TAB -----------------
if selected == "Analysis":
    st.subheader("Deeper Data Analysis")

    with st.expander("📊 Sales by Customer Type and Subscription", expanded=True):
        fig = px.box(filtered_df, x="Customer Type", y="Sales Amount", color="Subscription Type", title="Sales by Customer Type and Subscription")
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📉 Profit vs. Loss", expanded=False):
        profit_loss = filtered_df.groupby("Country")[["Profit", "Loss"]].sum().reset_index()
        fig = px.bar(profit_loss, x="Country", y=["Profit", "Loss"], barmode="group", title="Profit vs. Loss by Country")
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("🧮 Response Time vs Refund Amount", expanded=False):
        fig = px.scatter(filtered_df, x="Response Time (days)", y="Refund Amount", color="Product Type", title="Response Time vs Refund Amount")
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📌 Statistical Summary", expanded=False):
        st.dataframe(filtered_df.describe())

    with st.expander("🧾 Aggregated Overview", expanded=False):
        st.dataframe(filtered_df.groupby("Country")[["Sales Amount", "Profit", "Loss"]].agg(['sum', 'mean', 'count']))

# ----------------- LOGOUT -----------------
if selected == "Logout":
    if os.path.exists(COOKIE_FILE):
        os.remove(COOKIE_FILE)
    st.session_state.authenticated = False
    st.success("Logged out.")
    st.switch_page("login.py")
