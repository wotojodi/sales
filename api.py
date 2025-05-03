import os
import pandas as pd
import plotly.express as px
import streamlit as st
from io import BytesIO
from datetime import datetime
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
from Generating_data import create_record


# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Sales and Marketing Dashboard", layout="wide")

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

# ----------------- SALES TAB -----------------
if selected == "Sales":

    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter Options")
    country_filter = st.sidebar.multiselect("Select Country", options=df['Country'].unique())
    product_filter = st.sidebar.multiselect("Select Product", options=df['Product Type'].unique())
    year_filter = st.sidebar.multiselect("Select Year", options=df['Sales Date '].astype(str).str[:4].unique())

    # --- APPLY FILTERS ---
    filtered_df = df.copy()
    if country_filter:
        filtered_df = filtered_df[filtered_df['Country'].isin(country_filter)]
    if product_filter:
        filtered_df = filtered_df[filtered_df['Product Type'].isin(product_filter)]
    if year_filter:
        filtered_df = filtered_df[filtered_df['Sales Date '].astype(str).str[:4].isin(year_filter)]

    # --- EXPORT CSV ---
    st.subheader("Export Data")
    towrite = BytesIO()
    filtered_df.to_csv(towrite, index=False)
    towrite.seek(0)
    st.download_button(
        label="Export to CSV",
        data=towrite,
        file_name='AI_Solution_Dataset.csv',
        mime='text/csv'
    )

    # --- KPIs ---
    total_sales_revenue = filtered_df['Sales Amount'].sum()
    average_sale_amount = filtered_df['Sales Amount'].mean()
    total_profit = filtered_df['Profit'].sum()
    total_loss = filtered_df['Loss'].sum()
    net_profit = total_profit - total_loss
    total_job_request = filtered_df["Product Type"].count()

    with st.expander("📊 Key Performance Indicators", expanded=True):
        kpi_row1 = st.columns(3)
        kpi_row2 = st.columns(3)

        kpi_row1[0].metric(label="Total Sales Revenue", value=f"${total_sales_revenue:,.2f}")
        kpi_row1[1].metric(label="Total Profit", value=f"${total_profit:,.2f}")
        kpi_row1[2].metric(label="Total Loss", value=f"${total_loss:,.2f}")

        kpi_row2[0].metric(label="Net Profit", value=f"${net_profit:,.2f}")
        kpi_row2[1].metric(label="Total Job Request", value=total_job_request)
        kpi_row2[2].metric(label="Average Sales Amount", value=f"{average_sale_amount:,.2f}")

    # --- CHARTS ---
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

# ----------------- OTHER TABS -----------------
if selected == "Effectiveness":
    st.title("Effectiveness Analysis Coming Soon")

if selected == "Analysis":
    st.title("Deeper Data Analysis Coming Soon")

# ----------------- LOGOUT -----------------
if selected == "Logout":
    st.session_state.authenticated = False
    st.success("You have been logged out.")
