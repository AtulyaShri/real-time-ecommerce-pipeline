from faker import Faker
import pandas as pd
import random
import os

fake = Faker("en_IN")

# -----------------------------
# Configuration
# -----------------------------

NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 100

os.makedirs("data", exist_ok=True)


# -----------------------------
# Generate Customers
# -----------------------------

customers = []

cities = {
    "Madhya Pradesh": [
        "Bhopal",
        "Indore",
        "Gwalior",
        "Jabalpur"
    ],
    "Maharashtra": [
        "Mumbai",
        "Pune",
        "Nagpur"
    ],
    "Delhi": [
        "New Delhi"
    ],
    "Karnataka": [
        "Bengaluru",
        "Mysore"
    ],
    "Uttar Pradesh": [
        "Lucknow",
        "Kanpur",
        "Agra"
    ],
    "Rajasthan": [
        "Jaipur",
        "Udaipur",
        "Jodhpur"
    ]
}

for customer_id in range(
    1001,
    1001 + NUM_CUSTOMERS
):

    state = random.choice(
        list(cities.keys())
    )

    city = random.choice(
        cities[state]
    )

    customer = {
        "customer_id": customer_id,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "gender": random.choice([
            "Male",
            "Female"
        ]),
        "age": random.randint(
            18,
            65
        ),
        "city": city,
        "state": state,
        "signup_date": fake.date_between(
            start_date="-3y",
            end_date="today"
        )
    }

    customers.append(customer)


customers_df = pd.DataFrame(
    customers
)

customers_df.to_csv(
    "data/customers.csv",
    index=False
)


# -----------------------------
# Generate Products
# -----------------------------

product_categories = {

    "Electronics": [
        "Wireless Headphones",
        "Bluetooth Speaker",
        "Smart Watch",
        "Wireless Mouse",
        "Mechanical Keyboard",
        "Power Bank",
        "USB-C Cable"
    ],

    "Clothing": [
        "T-Shirt",
        "Jeans",
        "Hoodie",
        "Jacket",
        "Sneakers",
        "Formal Shirt"
    ],

    "Home": [
        "Table Lamp",
        "Bedsheet",
        "Coffee Mug",
        "Wall Clock",
        "Storage Box"
    ],

    "Books": [
        "Python Programming",
        "Data Engineering",
        "Machine Learning",
        "Database Systems",
        "Artificial Intelligence"
    ],

    "Fitness": [
        "Yoga Mat",
        "Dumbbells",
        "Resistance Band",
        "Skipping Rope",
        "Gym Gloves"
    ]
}

products = []

product_id = 2001

for category, product_names in product_categories.items():

    for product_name in product_names:

        products.append({
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "price": random.randint(
                199,
                15000
            ),
            "stock_quantity": random.randint(
                10,
                500
            )
        })

        product_id += 1


products_df = pd.DataFrame(
    products
)

products_df.to_csv(
    "data/products.csv",
    index=False
)


# -----------------------------
# Output
# -----------------------------

print(
    "Customer and product data generated successfully."
)

print(
    f"Total customers: {len(customers_df)}"
)

print(
    f"Total products: {len(products_df)}"
)