import time
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from faker import Faker
from io import BytesIO
import tornado.websocket
import tornado.iostream


# Initialize Faker to generate fake data
fake = Faker()

# Define job types and payment methods
job_types = ['Scheduled Demo', 'Prototyping solutions', 'AI-Powered Virtual Assistant', 'Software Assistance', 'Inquiring about Events', 'Chatting with Sales Representative']
payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer']

# Generate the dashboard

st.set_page_config(page_title="Sales and Marketing Dashboard", layout="wide")
st.title("Sales and Marketing Dashboard")



# Load the test data
@st.cache_data
def load_data():
    return pd.read_csv('product_sales_data.csv')
df = load_data()

# Sidebar for filtering
st.sidebar.header("Filter Options")
country_filter = st.sidebar.multiselect("Select Country", options=df['Country'].unique())
job_filter = st.sidebar.multiselect("Select Job Type", options=df['Job Requested'].unique())
demo_request_filter = st.sidebar.multiselect("Select Year", options=df['Year'].unique())
# Apply filters
if country_filter:
    df = df[df['Country'].isin(country_filter)]
if job_filter:
    df = df[df['Job Requested'].isin(job_filter)]
if demo_request_filter:
    df = df[df['Year'].isin(demo_request_filter)]

# Export functionality
st.subheader("Export Data")
towrite = BytesIO()
df.to_csv(towrite, index=False)
towrite.seek(0)
st.download_button(
    label="Export to CSV",
    data=towrite,
    file_name='exported_data.csv',
    mime='text/csv'
)

# Creating a single-element container for real-time updates
try:
    placeholder = st.empty()

    # Near real-time / live feed simulation
    for seconds in range(20):
        # Simulate new data by adding to existing columns
        df["Satisfaction Rating"] = df["Satisfaction Rating"] + np.random.choice(range(1, 5))
        df["Sales Revenue"] = np.random.uniform(100.0, 500.0, size=len(df))
        df["Job Requested"] = np.random.choice(job_types, size=len(df))
        df["Event Participation"] = np.random.choice(['Yes', 'No'], size=len(df))
        df["Resolution Status"] = np.random.choice(["Resolved", "Pending", "Failed"], size=len(df))

        # Calculate KPIs
        total_requests = df['Job Requested'].count()
        unique_countries = df['Country'].nunique()
        avg_satisfaction = df['Satisfaction Rating'].mean()
        event_participation_count = df[df["Event Participation"] == 'Yes'].shape[0]
        requests_for_scheduled_demos = df[df["Job Requested"] == "Scheduled Demo"].shape[0]
        requests_for_ai_assistant = df[df["Job Requested"] == "AI-Powered Virtual Assistant"].shape[0]
        requests_for_prototyping_solutions = df[df["Job Requested"] == "Prototyping solutions"].shape[0]
        balance = df["Sales Revenue"].sum()

        with placeholder.container():
            # Create two rows for KPIs
            kpi_row1 = st.columns(4)
            kpi_row2 = st.columns(4)

            # Display KPIs in the first row
            kpi_row1[0].metric(label="Total Requests", value=total_requests)
            kpi_row1[1].metric(label="Unique Countries", value=unique_countries)
            kpi_row1[2].metric(label="Average Satisfaction Rating", value=round(avg_satisfaction, 2))
            kpi_row1[3].metric(label="Total sales", value=round(balance, 2))

            # Display KPIs in the second row
            kpi_row2[0].metric(label="Total No of Event Participation", value=event_participation_count)
            kpi_row2[1].metric(label="Requests for Scheduled Demos", value=requests_for_scheduled_demos)
            kpi_row2[2].metric(label="Requests for AI Assistant", value=requests_for_ai_assistant)
            kpi_row2[3].metric(label="Requests for Prototyping Solutions", value=requests_for_prototyping_solutions)

            # Create 4 columns for charts
            fig_col1, fig_col2, fig_col3 = st.columns(3)

            with fig_col1:
                st.subheader("Sales over the Years")
                fig1 = px.bar(df, x='Year',y='Sales Revenue', title='Sales over the Years', color='Year')
                st.plotly_chart(fig1, key=f"RBJT_{seconds}")

            with fig_col2:
                st.subheader("Sales by Country")
                fig2 = px.choropleth(df,
                    locations='Country',
                    locationmode='country names',
                    color='Sales Revenue',
                    title='Sales Revenue by Country',
                    color_continuous_scale=px.colors.sequential.Plasma)
                st.plotly_chart(fig2, key=f"RBC_{seconds}")

            with fig_col3:
                st.subheader("Event Participation")
                fig3 = px.pie(df, names='Event Participation', values='Satisfaction Rating', title='Event Participation Satisfaction')
                st.plotly_chart(fig3, key=f"EP_{seconds}")

            
            # Create a new row for additional charts
            fig_col5, fig_col6, fig_col7 = st.columns(3)

            with fig_col5:
                st.subheader("Resolution Status by Job Requested")
                fig5 = px.bar(df, 
               x='Job Requested', 
               y='Resolution Status', 
               title='Resolution Status by Job Requested', 
               color='Resolution Status',
               category_orders={'Resolution Status': sorted(df['Resolution Status'].unique())})  # Ensuring order
                st.plotly_chart(fig5, key=f"RSJR_{seconds}")

            with fig_col6:
                st.subheader("Satisfaction per Job Requested")
                fig6 = px.histogram(df, x='Satisfaction Rating',y='Job Requested', title='Satisfaction Rating Distribution')
                st.plotly_chart(fig6, key=f"SPJR_{seconds}")

            with fig_col7:
                st.subheader("Job Requested")
                fig7 = px.bar(df, x='Job Requested', title='Job Requested', color='Job Requested')
                st.plotly_chart(fig7, key=f"SR_{seconds}")

    

            # Summary statistics
            st.subheader("Summary Statistics")
            summary_stats = df[['Sales Revenue', 'Satisfaction Rating']].agg(['mean', 'std', 'min', 'max'])
            st.dataframe(summary_stats)

        time.sleep(5)  # Delay for real-time simulation

except tornado.websocket.WebSocketClosedError:
    st.error("WebSocket connection closed unexpectedly.")
except tornado.iostream.StreamClosedError:
    st.error("Stream closed unexpectedly.")


