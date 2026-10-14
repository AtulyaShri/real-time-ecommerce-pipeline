import pandas as pd
import os
from datetime import datetime


# -----------------------------------
# Configuration
# -----------------------------------

DATA_PATH = "data"

os.makedirs("logs", exist_ok=True)


# -----------------------------------
# Logging
# -----------------------------------

log_file = (
    f"logs/validation_"
    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)


def log(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    message = f"[{timestamp}] {message}"

    print(message)

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(message + "\n")


# -----------------------------------
# Load data
# -----------------------------------

log("Starting data validation...")


customers = pd.read_csv(
    f"{DATA_PATH}/customers.csv"
)

products = pd.read_csv(
    f"{DATA_PATH}/products.csv"
)

orders = pd.read_csv(
    f"{DATA_PATH}/orders.csv"
)

payments = pd.read_csv(
    f"{DATA_PATH}/payments.csv"
)


# -----------------------------------
# Validation helper
# -----------------------------------

total_errors = 0


def check(
    condition,
    success_message,
    error_message
):

    global total_errors

    if condition:

        log(f"PASS: {success_message}")

    else:

        log(f"FAIL: {error_message}")

        total_errors += 1


# -----------------------------------
# CUSTOMER VALIDATION
# -----------------------------------

log("Validating customers...")


check(
    customers["customer_id"].notna().all(),
    "Customer IDs are not null.",
    "Customer IDs contain null values."
)


check(
    customers["customer_id"].is_unique,
    "Customer IDs are unique.",
    "Duplicate customer IDs found."
)


check(
    customers["first_name"].notna().all(),
    "Customer first names are valid.",
    "Missing customer first names found."
)


check(
    customers["email"].notna().all(),
    "Customer emails are not null.",
    "Missing customer emails found."
)


check(
    customers["email"].str.contains(
        "@",
        na=False
    ).all(),
    "Customer emails have valid format.",
    "Invalid customer email found."
)


check(
    customers["age"].between(
        18,
        100
    ).all(),
    "Customer ages are within valid range.",
    "Invalid customer age found."
)


# -----------------------------------
# PRODUCT VALIDATION
# -----------------------------------

log("Validating products...")


check(
    products["product_id"].notna().all(),
    "Product IDs are not null.",
    "Product IDs contain null values."
)


check(
    products["product_id"].is_unique,
    "Product IDs are unique.",
    "Duplicate product IDs found."
)


check(
    (products["price"] > 0).all(),
    "All product prices are greater than zero.",
    "Invalid product price found."
)


check(
    (products["stock_quantity"] >= 0).all(),
    "Stock quantities are valid.",
    "Invalid stock quantity found."
)


# -----------------------------------
# ORDER VALIDATION
# -----------------------------------

log("Validating orders...")


check(
    orders["order_id"].notna().all(),
    "Order IDs are not null.",
    "Order IDs contain null values."
)


check(
    orders["order_id"].is_unique,
    "Order IDs are unique.",
    "Duplicate order IDs found."
)


check(
    orders["customer_id"].isin(
        customers["customer_id"]
    ).all(),
    "All order customers exist.",
    "Order contains unknown customer IDs."
)


check(
    orders["product_id"].isin(
        products["product_id"]
    ).all(),
    "All ordered products exist.",
    "Order contains unknown product IDs."
)


check(
    (orders["quantity"] > 0).all(),
    "All order quantities are valid.",
    "Invalid order quantity found."
)


valid_order_statuses = {
    "Delivered",
    "Shipped",
    "Processing",
    "Cancelled"
}


check(
    orders["order_status"].isin(
        valid_order_statuses
    ).all(),
    "Order statuses are valid.",
    "Invalid order status found."
)


# -----------------------------------
# PAYMENT VALIDATION
# -----------------------------------

log("Validating payments...")


check(
    payments["payment_id"].notna().all(),
    "Payment IDs are not null.",
    "Payment IDs contain null values."
)


check(
    payments["payment_id"].is_unique,
    "Payment IDs are unique.",
    "Duplicate payment IDs found."
)


check(
    payments["order_id"].isin(
        orders["order_id"]
    ).all(),
    "All payments reference valid orders.",
    "Payment contains unknown order IDs."
)


check(
    (payments["amount"] > 0).all(),
    "Payment amounts are valid.",
    "Invalid payment amount found."
)


valid_payment_methods = {
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Cash on Delivery"
}


check(
    payments["payment_method"].isin(
        valid_payment_methods
    ).all(),
    "Payment methods are valid.",
    "Invalid payment method found."
)


valid_payment_statuses = {
    "Completed",
    "Pending",
    "Failed"
}


check(
    payments["payment_status"].isin(
        valid_payment_statuses
    ).all(),
    "Payment statuses are valid.",
    "Invalid payment status found."
)


# -----------------------------------
# FINAL RESULT
# -----------------------------------

log("-----------------------------------")

if total_errors == 0:

    log(
        "DATA VALIDATION SUCCESSFUL"
    )

    log(
        "All validation checks passed."
    )

else:

    log(
        f"DATA VALIDATION FAILED: "
        f"{total_errors} issue(s) found."
    )


log("-----------------------------------")