import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
num_transactions = 500
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 1, 31)

# Master data
stores = [
    {"store_id": "S1", "store_location": "Downtown"},
    {"store_id": "S2", "store_location": "Uptown"},
    {"store_id": "S3", "store_location": "Suburban"}
]

products = [
    {"product_id": "P101", "product_name": "Orange Juice 1L", "product_category": "Beverages", "unit_price": 3.5},
    {"product_id": "P102", "product_name": "Green Tea", "product_category": "Beverages", "unit_price": 2.8},
    {"product_id": "P103", "product_name": "Cola 2L", "product_category": "Beverages", "unit_price": 4.0},
    {"product_id": "P201", "product_name": "Potato Chips", "product_category": "Snacks", "unit_price": 1.2},
    {"product_id": "P202", "product_name": "Chocolate Bar", "product_category": "Snacks", "unit_price": 2.5},
    {"product_id": "P203", "product_name": "Cookies Pack", "product_category": "Snacks", "unit_price": 3.0},
    {"product_id": "P301", "product_name": "Shampoo 250ml", "product_category": "Personal Care", "unit_price": 4.0},
    {"product_id": "P302", "product_name": "Soap Bar", "product_category": "Personal Care", "unit_price": 1.5},
    {"product_id": "P303", "product_name": "Toothpaste", "product_category": "Personal Care", "unit_price": 2.2},
    {"product_id": "P401", "product_name": "Rice 5kg", "product_category": "Groceries", "unit_price": 8.5},
    {"product_id": "P402", "product_name": "Wheat Flour 2kg", "product_category": "Groceries", "unit_price": 5.0},
]

customer_segments = ["Regular", "New", "Loyal"]
payment_methods = ["Cash", "Credit Card", "UPI", "Debit Card"]
channels = ["In-store", "Online"]

# Generate data
data = []
bill_counter = 1001

for i in range(num_transactions):
    # Generate transaction details
    transaction_id = f"TXN-2025-{str(i+1).zfill(4)}"
    bill_id = f"BILL-{bill_counter}"
    
    # Random date
    days_diff = (end_date - start_date).days
    random_date = start_date + timedelta(days=random.randint(0, days_diff))
    date_str = random_date.strftime("%Y-%m-%d")
    
    # Random store
    store = random.choice(stores)
    
    # Random customer
    customer_id = f"C{str(random.randint(1, 100)).zfill(3)}"
    customer_segment = random.choice(customer_segments)
    
    # Random product
    product = random.choice(products)
    
    # Random quantity (1-5)
    quantity = random.randint(1, 5)
    
    # Payment method and channel
    payment_method = random.choice(payment_methods)
    channel = random.choice(channels)
    
    # Discount (20% chance of discount)
    discount_applied = round(random.uniform(0, 2), 2) if random.random() < 0.2 else 0.0
    
    # Create row
    row = {
        "transaction_id": transaction_id,
        "bill_id": bill_id,
        "date": date_str,
        "store_id": store["store_id"],
        "store_location": store["store_location"],
        "customer_id": customer_id,
        "customer_segment": customer_segment,
        "product_id": product["product_id"],
        "product_category": product["product_category"],
        "product_name": product["product_name"],
        "quantity": quantity,
        "unit_price": product["unit_price"],
        "payment_method": payment_method,
        "discount_applied": discount_applied,
        "channel": channel
    }
    
    data.append(row)
    
    # 30% chance to increment bill (new customer)
    if random.random() < 0.3:
        bill_counter += 1

# Create DataFrame and save
df = pd.DataFrame(data)
df.to_csv("urbanmart_sales.csv", index=False)

print(f"✅ Generated {len(df)} transactions")
print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
print(f"🏪 Stores: {df['store_id'].unique().tolist()}")
print(f"📦 Product categories: {df['product_category'].unique().tolist()}")
print(f"\n✅ File saved: urbanmart_sales.csv")