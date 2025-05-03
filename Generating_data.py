from faker import Faker
import pandas as pd
import numpy as np
import random
from datetime import date

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

# Function to create a single record
def create_record():
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



    return {

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
    }

# Generate dataset
data = [create_record() for _ in range(10000)]
df = pd.DataFrame(data)

# Reorder columns for clarity and decision-making
df = df[[

    "Customer ID",
    "Customer Name",
    "Email",
    "Phone",
    "Country",
    "Gender",
    "Age",
    "Company Name",
    "Customer Type",
    "Subscription Type",
    "Benefits of Membership Type",
    "Subscription Duration",
    "Subscription Price",
    "Product ID",
    "Product Type",
    "Inquries",
    "Sales Amount",
    "Sales Date ",
    "Sales Time",
    "Payment Method",
    "Demo Scheduled",
    "Promotional Event Participation",
    "Promotional Event",
    "Response Time (days)",
    "Product Status",
    "Refund Amount",
    "Comments",
    "Product Rating",
    "Profit",
    "Loss"
]]

# Save to CSV
df.to_csv('AI_Solutions_Dataset.csv', index=False)

# Display the first few records
print(df.head())