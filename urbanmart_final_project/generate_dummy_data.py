"""
generate_dummy_data.py

Small helper to generate a synthetic urbanmart_sales.csv file
aligned with the assignment's metadata.
"""

import random
from datetime import datetime, timedelta

import pandas as pd

random.seed(42)

num_rows = 1000

start_date = datetime(2025, 1, 1)
store_ids = ["S1", "S2", "S3"]
store_locations = {"S1": "Downtown", "S2": "Uptown", "S3": "Suburban"}
customer_segments = ["Regular", "New", "Loyal"]
product_categories = ["Beverages", "Snacks", "Personal Care"]
payment_methods = ["Cash", "Credit Card", "UPI"]
channels = ["In-store", "Online"]

records = []

for i in range(1, num_rows + 1):
    tx_date = start_date + timedelta(days=random.randint(0, 60))
    store_id = random.choice(store_ids)
    store_location = store_locations[store_id]

    customer_id = f"C{random.randint(1, 200):03d}"
    customer_segment = random.choice(customer_segments)

    product_category = random.choice(product_categories)
    product_id = f"P{random.randint(100, 399)}"

    product_name = {
        "Beverages": "Orange Juice 1L",
        "Snacks": "Potato Chips",
        "Personal Care": "Shampoo 250ml",
    }[product_category]

    quantity = random.randint(1, 5)
    unit_price = round(random.uniform(1.0, 10.0), 2)
    discount_applied = round(random.choice([0.0, 0.5, 1.0, 2.0]), 2)

    payment_method = random.choice(payment_methods)
    channel = random.choice(channels)

    bill_id = f"BILL-{1000 + random.randint(0, 300)}"
    transaction_id = f"TXN-2025-{i:04d}"

    records.append(
        {
            "transaction_id": transaction_id,
            "bill_id": bill_id,
            "date": tx_date.strftime("%Y-%m-%d"),
            "store_id": store_id,
            "store_location": store_location,
            "customer_id": customer_id,
            "customer_segment": customer_segment,
            "product_id": product_id,
            "product_category": product_category,
            "product_name": product_name,
            "quantity": quantity,
            "unit_price": unit_price,
            "payment_method": payment_method,
            "discount_applied": discount_applied,
            "channel": channel,
        }
    )

df = pd.DataFrame(records)
df.to_csv("urbanmart_sales.csv", index=False)
print("Generated urbanmart_sales.csv with", len(df), "rows.")
