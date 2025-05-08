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
        try:
            with open(COOKIE_FILE, "r") as f:
                cookie = json.load(f)
                if cookie.get("expiry_time", 0) > time.time():
                    return True
        except Exception:
            return False
    return False

def save_cookie():
    try:
        with open(COOKIE_FILE, "w") as f:
            cookie = {
                "authenticated": True,
                "expiry_time": time.time() + SESSION_DURATION
            }
            json.dump(cookie, f)
    except Exception as e:
        st.error(f"Error saving session cookie: {e}")

def clear_cookie():
    if os.path.exists(COOKIE_FILE):
        try:
            os.remove(COOKIE_FILE)
        except Exception as e:
            st.error(f"Error clearing session cookie: {e}")

# ----------------- LOGIN FORM -----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = load_cookie()

if not st.session_state.authenticated:
    st.title("🔒 Login Required")
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.authenticated = True
            save_cookie()
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials. Please try again.")
    st.stop()

# ----------------- AUTO-REFRESH -----------------
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
    # If the file doesn't exist, initialize with one record and header
    initial_df = pd.DataFrame([create_record()])
    initial_df.to_csv(CSV_PATH, index=False)

# ----------------- READ UPDATED DATA -----------------
df = pd.read_csv(CSV_PATH, on_bad_lines="skip")

# ----------------- NAVIGATION MENU -----------------
selected = option_menu(
    menu_title=None,
    options=["Sales", "Effectiveness", "Analysis", "Logout"],
    icons=["bar-chart-line", "graph-up-arrow", "clipboard-data", "box-arrow-right"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "orange", "font-size": "25px"},
        "nav-link": {"font-size": "22px", "text-align": "center", "margin": "0px 15px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#0a7e07", "color": "white"},
    }
)

st.title("📊 Sales and Marketing Dashboard")

if not df.empty:
    # ----------------- FILTERS -----------------
    st.sidebar.header("🔎 Filter Options")
    country_filter = st.sidebar.multiselect("Select Country", options=sorted(df['Country'].dropna().unique()))
    product_filter = st.sidebar.multiselect("Select Product", options=sorted(df['Product Type'].dropna().unique()))
    year_filter = st.sidebar.multiselect("Select Year", options=sorted(df['Sales Date'].astype(str).str[:4].dropna().unique()))

    filtered_df = df.copy()
    if country_filter:
        filtered_df = filtered_df[filtered_df['Country'].isin(country_filter)]
    if product_filter:
        filtered_df = filtered_df[filtered_df['Product Type'].isin(product_filter)]
    if year_filter:
        filtered_df = filtered_df[filtered_df['Sales Date'].astype(str).str[:4].isin(year_filter)]

    # ----------------- EXPORT CSV -----------------
    st.subheader("Export Filtered Data")
    towrite = BytesIO()
    filtered_df.to_csv(towrite, index=False)
    towrite.seek(0)
    st.download_button(
        label="⬇️ Export to CSV",
        data=towrite,
        file_name='AI_Solution_Dataset_filtered.csv',
        mime='text/csv'
    )

    # ----------------- SALES TAB -----------------
    if selected == "Sales":
        st.subheader("📈 Sales Overview")

        total_customers= filtered_df["Customer ID"].count()
        total_countries=filtered_df["Country"].nunique()
        total_sales_revenue = filtered_df.loc[filtered_df["Product Status"] == "Completed", "Sales Amount"].sum()
        total_profit = filtered_df['Profit'].sum()
        total_loss = filtered_df['Loss'].sum()
        total_job_request = filtered_df["Product Type"].count()
        subscribers = filtered_df[filtered_df["Subscription Type"].isin(["Premium", "Standard"])].shape[0]
        subscriptions_price=filtered_df.loc[filtered_df["Subscription Type"] != "Free", "Subscription Price"].sum()
        demo = filtered_df[filtered_df["Demo Scheduled"] == 'Yes'].shape[0]
        total_promotion= filtered_df[filtered_df["Promotional Event Participation"]== 'Yes'].shape[0]
        AI_assistant = filtered_df[filtered_df["Assistance Type"] == 'AI-powered virtual assistant'].shape[0]
        top_selling = filtered_df["Product Type"].value_counts().idxmax() if not filtered_df.empty else "N/A"
        sales_rep = filtered_df[filtered_df["Assistance Type"] == 'Sales Representative'].shape[0]

        with st.expander("📊 Key Performance Indicators", expanded=True):
            kpi_row1 = st.columns(3)
            kpi_row2 = st.columns(3)
            kpi_row3 = st.columns(3)
            kpi_row4 = st.columns(3)

            # Row 1 – Financial Outcomes
            kpi_row1[0].metric(label="Total Sales Revenue", value=f"${total_sales_revenue:,.2f}")
            kpi_row1[1].metric(label="Total Profit", value=f"${total_profit:,.2f}")
            kpi_row1[2].metric(label="Total Loss", value=f"${total_loss:,.2f}")

            # Row 2 – Sales Performance & Conversion
            kpi_row2[0].metric(label="Top Selling Product", value=top_selling)
            kpi_row2[1].metric(label="Total Subscriptions", value=subscribers)
            kpi_row2[2].metric(label="Subscription Revenue", value=f"${subscriptions_price:,.2f}")

            # Row 3 – Customer Reach & Engagement
            kpi_row3[0].metric(label="Total Customers", value=total_customers)
            kpi_row3[1].metric(label="Number of Countries", value=total_countries)
            kpi_row3[2].metric(label="Total Job Requests", value=total_job_request)

            # Row 4 – Support & Sales Channels
            kpi_row4[0].metric(label="Sales Rep Requests", value=sales_rep)
            kpi_row4[1].metric(label="AI Assistant Requests", value=AI_assistant)
            kpi_row4[2].metric(label="Promo Event Participations", value=total_promotion)

        # Section 1: Overall Financial Performance
        with st.expander("💰 Financial Performance", expanded=False):
            completed_df = filtered_df[filtered_df['Product Status'] == 'Completed']
            fig_col1, fig_col2, fig_col3 = st.columns(3)

            with fig_col1:
                fig1 = px.bar(
                    completed_df,
                    x=completed_df['Sales Date'].astype(str).str[:4],
                    y='Sales Amount',
                    title='Yearly Sales Revenue',
                    labels={"x":"Year","Sales Amount":"Sales Amount $"}
                )
                st.plotly_chart(fig1, use_container_width=True, dynamic=False)

            with fig_col2:
                fig2 = px.bar(
                    completed_df,
                    x='Product Type',
                    y='Profit',
                    title='Profit by Product Type',
                    labels={"Profit":"Profit $"}
                )
                st.plotly_chart(fig2, use_container_width=True, dynamic=False)

            with fig_col3:
                fig3 = px.bar(
                    filtered_df,
                    x='Product Type',
                    y='Loss',
                    title='Loss by Product Type',
                    labels={"Loss":"Loss $"}
                )
                st.plotly_chart(fig3, use_container_width=True, dynamic=False)

        # Section 2: Subscription Insights
        with st.expander("📦 Subscription Insights", expanded=False):
            fig_col4, fig_col5 = st.columns(2)

            with fig_col4:
                subscription_price_by_type = filtered_df.groupby('Subscription Type')['Subscription Price'].sum().reset_index()
                fig4 = px.pie(
                    subscription_price_by_type,
                    names='Subscription Type',
                    values='Subscription Price',
                    title='Revenue by Subscription Type'
                )
                st.plotly_chart(fig4, use_container_width=True, dynamic=False)

            with fig_col5:
                fig5 = px.histogram(
                    filtered_df,
                    x='Customer Type',
                    y='Sales Amount',
                    title='Customer Type vs Sales Amount',
                    labels={"Sales Amount":"Sales Amount $"}
                )
                st.plotly_chart(fig5, use_container_width=True, dynamic=False)

        # Section 3: Regional Sales Overview
        with st.expander("🌍 Regional Sales Overview", expanded=False):
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

            st.subheader("Customer Count by Country")
            customer_counts = filtered_df['Country'].value_counts().reset_index()
            customer_counts.columns = ['Country', 'Customer Count']

            fig_bar = px.bar(
                customer_counts,
                x='Customer Count',
                y='Country',
                orientation='h',
                title='Horizontal Bar: Customers by Country',
                color='Customer Count',
                color_continuous_scale='Teal'
            )
            fig_bar.update_layout(yaxis=dict(dtick=1))
            st.plotly_chart(fig_bar, use_container_width=True, dynamic=False)

    # ----------------- EFFECTIVENESS TAB -----------------
    if selected == "Effectiveness":
        st.subheader("📊 Effectiveness Analysis")

        def get_star_rating(rating):
            full_stars = int(rating)
            half_star = rating - full_stars >= 0.5
            stars = "⭐" * full_stars
            if half_star:
                stars += "✬"
            return stars

        avg_rating = filtered_df['Product Rating'].mean()
        stars = get_star_rating(avg_rating) if not filtered_df.empty else ""
        refund_rate = filtered_df['Refund Amount'].sum()
        avg_response_time = filtered_df['Response Time (days)'].mean()
        completed_product = filtered_df[filtered_df["Product Status"] == "Completed"].shape[0]
        canceled_product = filtered_df[filtered_df["Product Status"] == "Canceled"].shape[0]
        failed_product = filtered_df[filtered_df["Product Status"] == "Failed"].shape[0]

        with st.expander("📌 Effectiveness KPIs", expanded=True):
            kpis_row1 = st.columns(3)
            kpis_row2 = st.columns(3)

            kpis_row1[0].metric("Avg. Product Rating", f"{avg_rating:.2f}  {stars}")
            kpis_row1[1].metric("Refund Amount", f"${refund_rate:,.2f}")
            kpis_row1[2].metric("Avg. Response Time (days)", f"{avg_response_time:.2f}")

            kpis_row2[0].metric("Completed Products", value=completed_product)
            kpis_row2[1].metric("Canceled Products", value=canceled_product)
            kpis_row2[2].metric("Failed Products", value=failed_product)

        with st.expander("📊 Customer Satisfaction & Ratings", expanded=False):
            rating_counts = filtered_df["Product Rating"].value_counts().sort_index()
            fig_rating = px.bar(
                x=rating_counts.index,
                y=rating_counts.values,
                labels={"x":"Rating", "y":"Count"},
                title="Distribution of Product Ratings"
            )
            st.plotly_chart(fig_rating, use_container_width=True, dynamic=False)

            fig_box = px.box(
                filtered_df,
                x="Product Status",
                y="Product Rating",
                title="Product Rating by Completion Status"
            )
            st.plotly_chart(fig_box, use_container_width=True, dynamic=False)

        with st.expander("📊 Rating by Subscription Tier", expanded=False):
            fig_sub_rating = px.box(
                filtered_df,
                x="Subscription Type",
                y="Product Rating",
                title="Rating by Subscription Type"
            )
            st.plotly_chart(fig_sub_rating, use_container_width=True, dynamic=False)

        with st.expander("📊 Customer Response Time", expanded=False):
            fig_response = px.histogram(
                filtered_df,
                x="Response Time (days)",
                nbins=10,
                title="Distribution of Response Times"
            )
            st.plotly_chart(fig_response, use_container_width=True, dynamic=False)

        with st.expander("📊 Refund Analysis by Status", expanded=False):
            fig_refund = px.bar(
                filtered_df,
                x="Product Status",
                y="Refund Amount",
                title="Refund Amount by Product Status"
            )
            st.plotly_chart(fig_refund, use_container_width=True, dynamic=False)

    # ----------------- ANALYSIS TAB -----------------
    if selected == "Analysis":
        st.subheader("🧾 Deeper Data Analysis")

        with st.expander("Aggregated Financial Overview by Country", expanded=True):
            st.write("Summarizes total, average, and count for Sales Amount, Profit, and Loss per country.")
            aggregated_data = (
                filtered_df.groupby("Country")[["Sales Amount", "Profit", "Loss"]]
                .agg(['sum', 'mean', 'count'])
                .round(2)
            )
            st.dataframe(aggregated_data, use_container_width=True)

        with st.expander("Statistical Summary of Numerical Metrics", expanded=False):
            st.write("Key statistics overview of main numerical dataset columns.")
            st.dataframe(filtered_df.describe().round(2), use_container_width=True)

        with st.expander("Summary by Customer Type and Subscription", expanded=False):
            customer_summary = (
                filtered_df.groupby(["Customer Type", "Subscription Type"])[["Sales Amount", "Profit", "Loss"]]
                .agg(['sum', 'mean', 'count'])
                .round(2)
            )
            st.write("Sales, Profit, and Loss by Customer and Subscription Type")
            st.dataframe(customer_summary, use_container_width=True)

        with st.expander("Response Time & Refund Insight Table", expanded=False):
            response_refund = (
                filtered_df.groupby("Product Type")[["Response Time (days)", "Refund Amount"]]
                .agg(['mean', 'max', 'count'])
                .round(2)
            )
            st.write("Refund Amounts relative to Response Time by Product Type")
            st.dataframe(response_refund, use_container_width=True)

else:
    st.warning("No data available to display yet. Please wait for data generation.")

# ----------------- LOGOUT -----------------
if selected == "Logout":
    clear_cookie()
    st.session_state.authenticated = False
    st.success("🚪 Logged out successfully. Please refresh the page.")
    st.stop()
