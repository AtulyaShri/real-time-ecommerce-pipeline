import pandas as pd
import random
import os

orders = pd.read_csv(
    "data/orders.csv"
)

products = pd.read_csv(
    "data/products.csv"
)

payments = []

payment_id = 80001

for _, order in orders.iterrows():

    product = products[
        products["product_id"]
        == order["product_id"]
    ].iloc[0]

    amount = (
        order["quantity"]
        * product["price"]
    )

    payment = {
        "payment_id": payment_id,
        "order_id": order["order_id"],
        "payment_method": random.choice([
            "UPI",
            "Credit Card",
            "Debit Card",
            "Net Banking",
            "Cash on Delivery"
        ]),
        "payment_status": random.choices(
            [
                "Completed",
                "Pending",
                "Failed"
            ],
            weights=[
                90,
                7,
                3
            ]
        )[0],
        "amount": amount,
        "payment_date": order["order_date"]
    }

    payments.append(payment)

    payment_id += 1


payments_df = pd.DataFrame(
    payments
)

payments_df.to_csv(
    "data/payments.csv",
    index=False
)

print(
    "Payment data generated successfully."
)

print(
    f"Total payments: {len(payments_df)}"
)