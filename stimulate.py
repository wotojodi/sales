import time
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from Generating_data import create_record
from io import BytesIO
import os

# Set up the Streamlit app
st.set_page_config(page_title="Sales and Marketing Dashboard", layout="wide")
st.title("Sales and Marketing Dashboard")

DATA_FILE = 'product_sales_data.csv'

# Load or initialize DataFrame to session_state
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        # Create initial DataFrame with one record if file doesn't exist
        df = pd.DataFrame([create_record()])
        df.to_csv(DATA_FILE, index=False)
    return df

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# Placeholder for real-time updates
placeholder = st.empty()

# Simulate live appending of data
for iteration in range(20):
    # Generate 5 new records
    new_records = [create_record() for _ in range(5)]
    new_df = pd.DataFrame(new_records)

    # Append new data to session_state df
    st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)

    # Save updated df to CSV
    st.session_state.df.to_csv(DATA_FILE, index=False)

    # Display updated DataFrame
    placeholder.dataframe(st.session_state.df)

    # Calculate KPIs
    total_requests = st.session_state.df['Job Requested'].count()
    unique_countries = st.session_state.df['Country'].nunique()
    avg_satisfaction = st.session_state.df['Satisfaction Rating'].mean()
    balance = st.session_state.df["Sales Revenue"].sum()

    # Display KPIs
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Requests", value=total_requests)
    col2.metric(label="Unique Countries", value=unique_countries)
    col3.metric(label="Average Satisfaction Rating", value=f"{round(avg_satisfaction, 2)}")
    col4.metric(label="Total Sales", value=f"${round(balance, 2):,.2f}")

    # Plotting
    if 'Year' in st.session_state.df.columns and 'Sales Revenue' in st.session_state.df.columns:
        fig = px.bar(st.session_state.df, x='Year', y='Sales Revenue', title='Sales over Years')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Data for 'Year' or 'Sales Revenue' is missing.")

    time.sleep(1)  # Wait before next update