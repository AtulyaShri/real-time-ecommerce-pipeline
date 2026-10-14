import pandas as pd
import random
import os
from faker import Faker

fake = Faker()

NUM_ORDERS = 10000

customers = pd.read_csv(
    "data/customers.csv"
)

products = pd.read_csv(
    "data/products.csv"
)

orders = []

for order_id in range(
    50001,
    50001 + NUM_ORDERS
):

    customer = customers.sample(
        1
    ).iloc[0]

    product = products.sample(
        1
    ).iloc[0]

    quantity = random.randint(
        1,
        5
    )

    order = {
        "order_id": order_id,
        "customer_id": int(
            customer["customer_id"]
        ),
        "product_id": int(
            product["product_id"]
        ),
        "quantity": quantity,
        "order_date": fake.date_time_between(
            start_date="-1y",
            end_date="now"
        ),
        "order_status": random.choices(
            [
                "Delivered",
                "Shipped",
                "Processing",
                "Cancelled"
            ],
            weights=[
                70,
                15,
                10,
                5
            ]
        )[0]
    }

    orders.append(order)


orders_df = pd.DataFrame(
    orders
)

os.makedirs(
    "data",
    exist_ok=True
)

orders_df.to_csv(
    "data/orders.csv",
    index=False
)

print(
    "Order data generated successfully."
)

print(
    f"Total orders: {len(orders_df)}"
)