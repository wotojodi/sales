import time
import pandas as pd
import plotly.express as px
import streamlit as st
from io import BytesIO
import tornado.websocket
import tornado.iostream
import os
from datetime import datetime, timedelta
import random
from datetime import date
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
from faker import Faker
import pandas as pd
import numpy as np
import random

# ----------------- AUTHENTICATION CHECK -----------------
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("You are not logged in. Please go back and log in.")
    st.switch_page("login.py")

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Sales and Marketing Dashboard", layout="wide")

# Refresh every 1 seconds
#st_autorefresh(interval=1000, key="data_refresh")

# ----------------- LOAD DATA -----------------
@st.cache_data()  
def load_data():
    return pd.read_csv('AI_Solutions_Dataset.csv',on_bad_lines="skip")
df = load_data()


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
# Initialize Faker
fake = Faker()

# Function to generate a phone number based on country
def generate_phone_number(country):
    if country == "USA":
        return fake.phone_number().split('x')[0]  # Remove extension if present
    elif country == "UK":
        return fake.phone_number().split('x')[0]  # Remove extension if present
    elif country == "Canada":
        return fake.phone_number() .split('x')[0]  # Remove extension if present
    elif country == "Australia":
        return fake.phone_number()  .split('x')[0]  # Remove extension if present
    else:
        return fake.phone_number().split('x')[0]  # Default format for other countries , remove extension if present

st.title("Sales and Marketing Dashboard")

# ----------------- SALES TAB -----------------
if selected == "Sales":
    # Sidebar filters
    st.sidebar.header("Filter Options")
    country_filter = st.sidebar.multiselect("Select Country", options=df['Country'].unique())
    product_filter = st.sidebar.multiselect("Select Product", options=df['Product Type'].unique())
    year_filter = st.sidebar.multiselect("Select Year", options=df['Sales Date '].str[:4].unique())

    # Apply filters
    if country_filter:
        df = df[df['Country'].isin(country_filter)]
    if product_filter:
        df = df[df['Product Type'].isin(product_filter)]
    if year_filter:
        df = df[df['Sales Date '].str[:4].isin(year_filter)]

    

    # Backup directory
    BACKUP_DIR = "backups"
    os.makedirs(BACKUP_DIR, exist_ok=True)

    if 'last_backup_date' not in st.session_state:
        st.session_state.last_backup_date = datetime.now() - timedelta(days=1)

    def backup_data(df):
        backup_filename = os.path.join(BACKUP_DIR, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(backup_filename, index=False)
        st.success(f"Backup created: {backup_filename}")

    try:
        placeholder = st.empty()

       # Near real-time / live feed simulation
        for seconds in range(200):
            # Generate new customer data
            new_data = []
            for _ in range(5):  # Generate 5 new customer records
                country = fake.country()
                phone = generate_phone_number(country)  # Generate phone number based on country
                customer_id = fake.uuid4()
                customer_name = fake.name()
                email = fake.email()
                gender = random.choice(['Male', 'Female'])
                age = random.randint(18, 65)
                Company_Name = fake.company()

                customer_type = random.choice(['Member'])
                Benefits_of_Membership_Type = random.choice([ 'Basic support', 'Exclusive offers'])
                Subscription_Duration = random.choice(['Monthly', 'Yearly'])
                Subscription_Date = fake.date_between(start_date=date(2022, 1, 1), end_date=date(2025, 12, 31))


                # Fixed subscription prices
                subscription_type = random.choice(['Premium', 'Standard', 'Free'])
                if subscription_type == 'Premium':
                    price = 50.00
                elif subscription_type == 'Standard':
                    price = 25.00
                else:
                    price = 0.00  # No subscription price for free

                Product_ID = random.randint(100, 200)

                # Product type (corrected to reflect the company's offerings)
                product_type = random.choice([
                    'Prototyping Tool', 'Design Software','Project Management Suite','Collaboration Platform','Data Analytics Tool','Customer Relationship Management (CRM) Software',
                    'Marketing Automation Tool','E-commerce Platform','Content Management System (CMS)','Accounting Software','Human Resources Management System (HRMS)','Inventory Management System','Email Marketing Software',
                    'Website Builder','Video Conferencing Tool','Task Management App','Social Media Management Tool','Cloud Storage Solution','Cybersecurity Software','Artificial Intelligence (AI) Analytics Tool','Chatbot and Conversational AI Platforms',
                    'Video Editing Software', 'Document Management System','Learning Management System (LMS)','Point of Sale (POS) Systems','Supply Chain Management Software',
                    'Business Intelligence (BI) Tools', 'Graphic Design Software','Mobile App Development Platforms', 'Event Management Software','Performance Management Software'

                ])
                Inquiry_Type = random.choice(['Product question', 'Promotional event', 'Issue with product'])


                # Cost of service/product (randomly generated)
                cost_of_service = round(np.random.uniform(20, 100), 2)  # Random cost between 20 and 100
                sales_date = fake.date_between(start_date=date(2022, 1, 1), end_date=date(2025, 12, 31))
                sales_time = fake.time()
                demo_scheduled = random.choice(['Yes', 'No'])
                Promotional_Event_Participation = random.choice(['Yes', 'No'])
                Type_of_Promotional_Event = random.choice(['AI Technology Expos', 'Workshops on Prototyping Solutions', 'Webinars on AI Integration in Business','Panel Discussions with AI Experts','AI-Driven Marketing Strategy Sessions'])

                price_of_service = round(np.random.uniform(150, 300), 2)  # Random service price
                response_time = random.randint(1, 10)  # Response time in days
                product_status = random.choice(['Completed', 'Canceled', 'Failed'])
                refund_amount = 0.0

                comments = ""  # Initialize comments to an empty string

                # Generate product rating based on product status
                if product_status == 'Completed':
                    product_rating = random.randint(3, 5)  # Any rating for completed products
                else:
                    product_rating = random.choice([1, 2])  # Low rating for canceled or failed

                # Initialize profit and loss to 0 to avoid UnboundLocalError
                profit = 0.0
                loss = 0.0

                # Generate relevant comments based on product status and rating
                if product_status == 'Completed':
                    refund_amount = 0.0  # No refund
                    profit = price_of_service  - cost_of_service
                    loss = 0.0 if profit >= 0 else abs(profit)

                    # Generate relevant comments based on the product rating
                    if product_rating >= 4:
                        comments = fake.sentence(ext_word_list=["Excellent", "Great", "Loved", "Fantastic", "Highly recommend", "Will buy again"])
                    elif product_rating == 3:
                        comments = fake.sentence(ext_word_list=["Average", "Okay", "Not bad", "Could be better"])
                    else:
                        comments = fake.sentence(ext_word_list=["Disappointed", "Not satisfied", "Would not recommend", "Poor quality", "Did not meet expectations"])

                elif product_status == 'Canceled':
                    cancellation_fee = 20.0  # Flat cancellation fee, example
                    refund_amount = max(0.0, price_of_service - cancellation_fee)  # Refund minus cancellation fee
                    profit = refund_amount - cost_of_service  # Simplified profit
                    loss = 0.0 if profit >= 0 else abs(profit)
                    comments = fake.sentence(ext_word_list=["Cancellation due to delays.", "Did not deliver on the expected date.", "Service was not as described.", "Unhappy with the customer support.", "Decided to cancel due to poor communication."])

                elif product_status == 'Failed':
                    refund_amount = price_of_service  # Full refund if failed
                    loss = cost_of_service + refund_amount
                    comments = fake.sentence(ext_word_list=["Extremely disappointed!", "Product failed to meet expectations.", "Would not recommend this product.", "Very poor quality!", "Did not work as promised."])


                # Updated payment methods for online transactions
                payment_methods = ['Credit Card', 'PayPal', 'Skrill','Airpay']
                payment_method = random.choice(payment_methods)


                new_data.append({
                    "Customer ID": customer_id,
                    "Customer Name": customer_name,
                    "Email": email,
                    "Phone": phone,
                    "Country": country,
                    "Gender": gender,
                    "Age": age,
                    "Company Name": Company_Name,
                    "Customer Type": customer_type,
                    "Subscription Type": subscription_type,
                    "Benefits of Membership Type": Benefits_of_Membership_Type,
                    "Subscription Duration": Subscription_Duration,
                    "Subscription Date": Subscription_Date,
                    "Subscription Price": price,
                    "Product ID":Product_ID,
                    "Product Type": product_type,
                    "Inquries": Inquiry_Type,
                    "Cost of Product": cost_of_service,
                    "Sales Amount": price_of_service,
                    "Sales Date ": sales_date,
                    "Sales Time": sales_time,
                    "Payment Method": payment_method,
                    "Demo Scheduled": demo_scheduled,
                    "Promotional Event Participation": Promotional_Event_Participation,
                    "Promotional Event":Type_of_Promotional_Event,
                    "Response Time (days)": response_time,
                    "Product Status": product_status,
                    "Refund Amount": refund_amount,
                    "Product Rating": product_rating,
                    "Comments": comments,
                    "Profit": profit,
                    "Loss": loss
                })

            # Convert new data to DataFrame
            new_df = pd.DataFrame(new_data)

            # Format the Sales Date column as string (if it's a datetime or date object)
            if 'Sales Date ' in new_df.columns:
                new_df['Sales Date '] = pd.to_datetime(new_df['Sales Date ']).dt.strftime('%Y-%m-%d')

            # Append the new data to the existing DataFrame in memory (for live dashboard updates)
            df = pd.concat([df, new_df], ignore_index=True)

            # Display the updated DataFrame in Streamlit
            placeholder.dataframe(df)

            # Append only the new data to the CSV file (avoid overwriting)
            new_df.to_csv('AI_Solutions_Dataset.csv', mode='a', header=False, index=False)
            

            total_sales_revenue = df['Sales Amount'].sum()
            average_sale_amount = df['Sales Amount'].mean()
            total_profit = df['Profit'].sum()
            total_loss = df['Loss'].sum()
            net_profit = total_profit - total_loss
            total_job_request = df["Product Type"].count()
            total_records = len(df)


            with placeholder.container():
                with st.expander("📊 Key Performance Indicators", expanded=True):
                    kpi_row1 = st.columns(3)
                    kpi_row2 = st.columns(3)

                    kpi_row1[0].metric(label="Total Sales Revenue", value=f"${total_sales_revenue:,.2f}")
                    kpi_row1[1].metric(label="Total Profit", value=f"${total_profit:,.2f}")
                    kpi_row1[2].metric(label="Total Loss", value=f"${total_loss:,.2f}")

                    kpi_row2[0].metric(label="Net Profit", value=f"${net_profit:,.2f}")
                    kpi_row2[1].metric(label="Total Job Request", value=total_job_request)
                    kpi_row2[2].metric(label="Average Sales Amount", value=f"{average_sale_amount:,.2f}")

                    kpi_row3=st.columns(1)

                    kpi_row3[0].metric(label="Total Records", value=total_records)


                with st.expander("📈 Sales & Profit Visualizations", expanded=False):
                    fig_col1, fig_col2, fig_col3 = st.columns(3)

                    with fig_col1:
                        fig1 = px.bar(df, x=df['Sales Date '].str[:4], y='Sales Amount', title='Sales over the Years')
                        st.plotly_chart(fig1, use_container_width=True, key=f"RBJT_{seconds}")

                    with fig_col2:
                        fig2 = px.choropleth(
                            df, locations='Country', locationmode='country names',
                            color='Sales Amount', title='Sales Revenue by Country',
                            color_continuous_scale=px.colors.sequential.Plasma
                        )
                        st.plotly_chart(fig2, use_container_width=True, key=f"RBC_{seconds}")

                    with fig_col3:
                        fig3 = px.bar(df, x='Product Type', y='Profit', title='Profit by Product')
                        st.plotly_chart(fig3, use_container_width=True, key=f"EP_{seconds}")

                with st.expander("📉 Loss & Subscriptions Visualizations", expanded=False):
                    fig_col5, fig_col6, fig_col7 = st.columns(3)

                    with fig_col5:
                        fig5 = px.bar(df, x='Product Type', y='Loss', title="Loss by Product")
                        st.plotly_chart(fig5, use_container_width=True, key=f"RSJR_{seconds}")

                    with fig_col6:
                        fig6 = px.histogram(df, x='Customer Type', y='Sales Amount', title='Customer Type by Sales Amount')
                        st.plotly_chart(fig6, use_container_width=True, key=f"SPJR_{seconds}")

                    with fig_col7:
                        subscription_price_by_type = df.groupby('Subscription Type')['Subscription Price'].sum().reset_index()
                        fig7 = px.pie(
                            subscription_price_by_type,
                            names='Subscription Type',
                            values='Subscription Price',
                            title='Total Subscription Price by Subscription Type'
                        )
                        st.plotly_chart(fig7, use_container_width=True, key=f"SR_{seconds}")
                with st.expander("Data View", expanded=False):
    
                    st.markdown("### Detailed Data View")
                    st.dataframe(df)

            time.sleep(1)
        
    except tornado.websocket.WebSocketClosedError:
        st.error("WebSocket connection closed unexpectedly.")
    except tornado.iostream.StreamClosedError:
        st.error("Stream closed unexpectedly.")
    

# ----------------- OTHER TABS -----------------
if selected == "Effectiveness":

    st.title("Effectiveness Analysis")

    with st.expander("🎯 Product Rating Distribution", expanded=True):
        
        # Count ratings
        rating_counts = df["Product Rating"].value_counts().sort_index()

        fig_rating = px.bar(x=rating_counts.index,y=rating_counts.values, title="Distribution of Product Ratings")
        st.plotly_chart(fig_rating, use_container_width=True)

    with st.expander("🧠 Effectiveness by Product Status", expanded=False):
        fig_status_rating = px.box(df, x="Product Status", y="Product Rating", title="Product Rating by Status")
        st.plotly_chart(fig_status_rating, use_container_width=True)

    with st.expander("📍Product Status vs Refund Amount", expanded=False):
        fig_refund = px.bar(df, x="Product Status", y="Refund Amount", title="Refund Amount by Product Status")
        st.plotly_chart(fig_refund, use_container_width=True)

    with st.expander("📆 Response Time Effectiveness", expanded=False):
        fig_response = px.histogram(df, x="Response Time (days)", nbins=10, title="Distribution of Customer Response Times")
        st.plotly_chart(fig_response, use_container_width=True)

    with st.expander("📦 Rating by Subscription Type", expanded=False):
        fig_sub_rating = px.box(df, x="Subscription Type", y="Product Rating", title="Product Rating by Subscription Type")
        st.plotly_chart(fig_sub_rating, use_container_width=True)

    with st.expander("🌍 Avg Product Rating by Country", expanded=False):
        avg_rating_country = df.groupby("Country")["Product Rating"].mean().reset_index()
        fig_rating_country = px.bar(avg_rating_country.sort_values("Product Rating", ascending=False),
        x="Country", y="Product Rating", title="Average Product Rating by Country")
        st.plotly_chart(fig_rating_country, use_container_width=True)

    

    with st.expander("📉 Low Rated Product Types", expanded=False):
        low_rating_df = df[df["Product Rating"] <= 2]
        low_rating_count = low_rating_df["Product Type"].value_counts().reset_index()
        low_rating_count.columns = ["Product Type", "Low Rating Count"]
        fig_low_rating = px.bar(low_rating_count, x="Product Type", y="Low Rating Count",
        title="Low Ratings by Product Type")
        st.plotly_chart(fig_low_rating, use_container_width=True)


if selected == "Analysis":
    st.title("Deeper Data Analysis Coming Soon")

# ----------------- LOGOUT -----------------
if selected == "Logout":
    st.session_state.authenticated = False
    st.success("You have been logged out.")
    st.switch_page("login.py")
