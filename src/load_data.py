import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


# ---------------------------------
# Load environment variables
# ---------------------------------

load_dotenv()


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ---------------------------------
# Database connection
# ---------------------------------

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# ---------------------------------
# Extract
# ---------------------------------

print("Starting data extraction...")


customers = pd.read_csv(
    "data/customers.csv"
)

products = pd.read_csv(
    "data/products.csv"
)

orders = pd.read_csv(
    "data/orders.csv"
)

payments = pd.read_csv(
    "data/payments.csv"
)


print(f"Customers extracted: {len(customers)}")
print(f"Products extracted: {len(products)}")
print(f"Orders extracted: {len(orders)}")
print(f"Payments extracted: {len(payments)}")


# ---------------------------------
# Transform
# ---------------------------------

print("\nStarting transformation...")


# Remove duplicate records

customers = customers.drop_duplicates(
    subset=["customer_id"]
)

products = products.drop_duplicates(
    subset=["product_id"]
)

orders = orders.drop_duplicates(
    subset=["order_id"]
)

payments = payments.drop_duplicates(
    subset=["payment_id"]
)


# Convert dates

customers["signup_date"] = pd.to_datetime(
    customers["signup_date"]
)

orders["order_date"] = pd.to_datetime(
    orders["order_date"]
)

payments["payment_date"] = pd.to_datetime(
    payments["payment_date"]
)


# Clean text fields

customers["first_name"] = (
    customers["first_name"]
    .astype(str)
    .str.strip()
)

customers["last_name"] = (
    customers["last_name"]
    .astype(str)
    .str.strip()
)

customers["email"] = (
    customers["email"]
    .astype(str)
    .str.strip()
    .str.lower()
)


# ---------------------------------
# Load
# ---------------------------------

print("\nLoading data into PostgreSQL...")


customers.to_sql(
    "customers",
    engine,
    if_exists="append",
    index=False
)

products.to_sql(
    "products",
    engine,
    if_exists="append",
    index=False
)

orders.to_sql(
    "orders",
    engine,
    if_exists="append",
    index=False
)

payments.to_sql(
    "payments",
    engine,
    if_exists="append",
    index=False
)


print("\nETL pipeline completed successfully.")