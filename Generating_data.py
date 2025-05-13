from faker import Faker
import pandas as pd
import numpy as np
import random
from datetime import date
import phonenumbers
from phonenumbers import geocoder, carrier
from phonenumbers.phonenumberutil import region_code_for_country_code
import csv


# Initialize Faker
fake = Faker()

# Function to get a properly formatted international phone number
def generate_phone_number(country):
    try:
        # Generate a fake phone number
        number = fake.phone_number()
        
        # Try to get the country code for the given country
        country_code = phonenumbers.country_code_for_region(fake.country_code(representation="alpha-2"))

        # Parse and reformat the number with the country code
        parsed_number = phonenumbers.parse(number, None)
        
        # If number is valid, format in E.164 (e.g., +14155552671)
        if phonenumbers.is_valid_number(parsed_number):
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        else:
            # Fallback: just add country code manually and strip invalid characters
            clean_number = ''.join(filter(str.isdigit, number))
            return f"+{country_code}{clean_number[-10:]}"  # Use last 10 digits assuming it's a mobile number
    except:
        # Fallback if formatting fails
        return f"+{random.randint(1, 199)}{random.randint(1000000000, 9999999999)}"

# Function to create a single record
def create_record():
    country = fake.country()
    phone = generate_phone_number(country)
    customer_id = fake.uuid4()
    customer_name = fake.name()
    email = fake.email()
    gender = random.choice(['Male', 'Female'])
    age = random.randint(18, 65)
    Company_Name = fake.company()
    customer_type = random.choice(['Subscriber', 'Non-Subscriber'])
    Benefits_of_Membership_Type = random.choice(['Basic support', 'Exclusive offers'])
    Subscription_Duration = random.choice(['Monthly', 'Yearly'])
    Subscription_Date = fake.date_between(start_date=date(2022, 1, 1), end_date=date(2025, 12, 31))
    subscription_type = random.choice(['Premium', 'Standard', 'Free'])
    price = 50.0 if subscription_type == 'Premium' else 25.0 if subscription_type == 'Standard' else 0.0
    Product_ID = random.randint(100, 200)
    product_type = random.choice([
        'Prototyping Tool', 'Design Software', 'Project Management Suite', 'Collaboration Platform',
        'Data Analytics Tool', 'Customer Relationship Management (CRM) Software', 'Marketing Automation Tool',
        'E-commerce Platform', 'Content Management System (CMS)', 'Accounting Software',
        'Human Resources Management System (HRMS)', 'Inventory Management System', 'Email Marketing Software',
        'Website Builder', 'Video Conferencing Tool', 'Task Management App', 'Social Media Management Tool',
        'Cloud Storage Solution', 'Cybersecurity Software', 'Artificial Intelligence (AI) Analytics Tool',
        'Chatbot and Conversational AI Platforms', 'Video Editing Software', 'Document Management System',
        'Learning Management System (LMS)', 'Point of Sale (POS) Systems', 'Supply Chain Management Software',
        'Business Intelligence (BI) Tools', 'Graphic Design Software', 'Mobile App Development Platforms',
        'Event Management Software', 'Performance Management Software'])
    Inquiry_Type = random.choice(['Product question', 'Promotional event', 'Issue with product'])
    cost_of_service = round(np.random.uniform(20, 100), 2)
    sales_date = fake.date_between(start_date=date(2022, 1, 1), end_date=date(2025, 12, 31))
    sales_time = fake.time()
    demo_scheduled = random.choice(['Yes', 'No'])
    Promotional_Event_Participation = random.choice(['Yes', 'No'])
    Type_of_Promotional_Event = random.choice([
        'AI Technology Expos', 'Workshops on Prototyping Solutions', 'Webinars on AI Integration in Business',
        'Panel Discussions with AI Experts', 'AI-Driven Marketing Strategy Sessions'])
    price_of_service = round(np.random.uniform(150, 300), 2)
    response_time = random.randint(1, 10)
    product_status = random.choice(['Completed', 'Canceled', 'Failed'])
    refund_amount = 0.0
    comments = ""
    if product_status == 'Completed':
        refund_amount = 0.0
        profit = price_of_service - cost_of_service
        loss = 0.0 if profit >= 0 else abs(profit)
        product_rating = random.randint(3, 5)
        comments = fake.sentence(ext_word_list=["Excellent", "Great", "Loved", "Fantastic", "Highly recommend", "Will buy again"] if product_rating >= 4 else ["Average", "Okay", "Not bad", "Could be better"])
    elif product_status == 'Canceled':
        cancellation_fee = 20.0
        refund_amount = max(0.0, price_of_service - cancellation_fee)
        profit = refund_amount - cost_of_service
        loss = 0.0 if profit >= 0 else abs(profit)
        product_rating = random.choice([1, 2])
        comments = fake.sentence(ext_word_list=["Cancellation due to delays.", "Service was not as described."])
    else:
        refund_amount = price_of_service
        loss = cost_of_service + refund_amount
        profit = 0.0
        product_rating = random.choice([1, 2])
        comments = fake.sentence(ext_word_list=["Extremely disappointed!", "Product failed to meet expectations."])
    payment_method = random.choice(['Credit Card', 'PayPal', 'Skrill', 'Airpay'])
    assistance_type = random.choice(["AI-powered virtual assistant", "Sales Representative"])
    # Add salesperson details if not AI-assisted
    Sales_Rep_Name=fake.name() if assistance_type == "Sales Representative" else "N/A"
    Sales_Rep_Email= fake.email() if assistance_type == "Sales Representative" else "N/A"
    Sales_Rep_Phone = fake.phone_number() if assistance_type == "Sales Representative" else "N/A"
    Sales_Rep_ID = fake.uuid4() if assistance_type == "Sales Representative" else "N/A"
    
    return {
        "Customer ID": customer_id, "Customer Name": customer_name, "Email": email, "Phone": phone, "Country": country,
        "Gender": gender, "Age": age, "Company Name": Company_Name, "Customer Type": customer_type,
        "Subscription Type": subscription_type, "Benefits of Membership Type": Benefits_of_Membership_Type,
        "Subscription Duration": Subscription_Duration, "Subscription Date": Subscription_Date,
        "Subscription Price": price, "Product ID": Product_ID, "Product Type": product_type,
        "Inquries": Inquiry_Type, "Assistance Type": assistance_type,  "Sales Rep ID":Sales_Rep_ID , "Sales Rep Name": Sales_Rep_Name, "Sales Rep Email":Sales_Rep_Email, "Sales Rep Phone":Sales_Rep_Phone, "Cost of Product": cost_of_service, "Sales Amount": price_of_service,
        "Sales Date": sales_date, "Sales Time": sales_time, "Payment Method": payment_method,
        "Demo Scheduled": demo_scheduled, "Promotional Event Participation": Promotional_Event_Participation,
        "Promotional Event": Type_of_Promotional_Event, "Response Time (days)": response_time,
        "Product Status": product_status, "Refund Amount": refund_amount, "Product Rating": product_rating,
        "Comments": comments, "Profit": profit, "Loss": loss
    }
# Column order
columns = [
    "Customer ID", "Customer Name", "Email", "Phone", "Country", "Gender", "Age",
    "Company Name", "Customer Type", "Subscription Type", "Benefits of Membership Type",
    "Subscription Duration", "Subscription Date", "Subscription Price", "Product ID",
    "Product Type", "Inquries", "Assistance Type", "Sales Rep ID", "Sales Rep Name",
    "Sales Rep Email", "Sales Rep Phone", "Cost of Product", "Sales Amount", "Sales Date",
    "Sales Time", "Payment Method", "Demo Scheduled", "Promotional Event Participation",
    "Promotional Event", "Response Time (days)", "Product Status", "Refund Amount",
    "Product Rating", "Comments", "Profit", "Loss"
]

# Create CSV and write header if it doesn't exist
filename = 'AI_Solution_Dataset.csv'
try:
    with open(filename, 'x', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
except FileExistsError:
    pass
