import csv
import random
from faker import Faker

# Initialize Faker for generating realistic data
fake = Faker()

# Sample data
countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Australia', 'India', 'Brazil','Spain','Japan','Portugal','Zimbabwe','Zambia','Russia','Netherlands','China','Jamaica']
job_types = ['Scheduled Demo', 'Prototyping solutions', 'AI-Powered Virtual Assistant','Software Assistence','Inquiring about events','Chatting with Sales Representative']
demo_requests = ['Scheduled Demo', 'Promotional Event', 'AI-Powered Virtual Assistant']
payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Debit Card']

# Number of records to generate
num_records = 10000

# Country to Faker locale mapping
country_locale_map = {
    "United States": "en_US",
    "United Kingdom": "en_GB",
    "India": "en_IN",
    "France": "fr_FR",
    "Germany": "de_DE",
    "Japan": "ja_JP",
    "South Africa": "en_ZA",
    "Italy": "it_IT",
    "Mexico": "es_MX",
    "Brazil": "pt_BR",
    "China": "zh_CN",
    "Russia": "ru_RU",
    "Canada": "en_CA",
    "Nigeria": "en_NG",
    "Kenya": "en_KE",
    "Philippines": "en_PH",
    "Australia": "en_AU"
}



# Generate realistic data
data = []
for _ in range(num_records):
    year = random.randint(2022, 2025)
    country = random.choice(countries)
    Customer_name=fake.name()
    Email=fake.email()
    job_requested = random.choice(job_types)  # Random job type requested
    Event_Participation= random.choice(['Yes', 'No'])
    page_accessed = random.choice(['/index.html', '/images/events.jpg', '/event.php', '/scheduledemo.php', '/prototype.php'])
    payment_method = random.choice(payment_methods)  # Random payment method
    Resolution_status=random.choice(["Resolved", "Pending", "Failed"])
    satisfaction_rating = random.randint(1, 5)  # Random satisfaction rating (1 to 5)

    # Generate phone number using country-specific locale
    locale = country_locale_map.get(country, 'en_US')
    localized_fake = Faker(locale)
    Phone_number = localized_fake.phone_number()

    # Adjust sales revenue based on resolution status
    if Resolution_status == 'Resolved':
        sales_revenue = round(random.uniform(1000, 10000), 2)# Full amount for resolved
    elif Resolution_status == 'Pending':
      sales_revenue = round(random.uniform(1000, 10000) / 2, 2) # Half amount for pending
    else:
      sales_revenue = 0.00 # No amount for failed

    data.append({
        'Year': year,
        'Country': country,
        'Customer Name':Customer_name,
        'Email':Email,
        'Phone Number':Phone_number,
        'Job Requested': job_requested,
        'Event Participation' : Event_Participation,
        'Page Accessed': page_accessed,
        'Sales Revenue': sales_revenue,
        'Payment Method': payment_method,
        'Resolution Status': Resolution_status,
        'Satisfaction Rating': satisfaction_rating
    })

# Specify the CSV file name
csv_file = 'product_sales_data.csv'

# Write to CSV
with open(csv_file, mode='w', newline='') as file:
    fieldnames = ['Year', 'Country','Customer Name','Email','Phone Number' ,'Job Requested','Event Participation','Page Accessed',  'Sales Revenue', 'Payment Method','Resolution Status', 'Satisfaction Rating']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(data)

print(f"Data generated and saved to {csv_file}")

