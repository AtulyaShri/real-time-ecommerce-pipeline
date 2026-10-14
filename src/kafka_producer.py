import json
import time

import pandas as pd
from kafka import KafkaProducer


# ---------------------------------
# Kafka configuration
# ---------------------------------

KAFKA_SERVER = "localhost:9092"

TOPIC_NAME = "ecommerce_orders"


# ---------------------------------
# Create Kafka producer
# ---------------------------------

producer = KafkaProducer(

    bootstrap_servers=KAFKA_SERVER,

    value_serializer=lambda value:
        json.dumps(value).encode("utf-8")
)


# ---------------------------------
# Load order data
# ---------------------------------

orders = pd.read_csv(
    "data/orders.csv"
)


print(
    f"Loaded {len(orders)} orders."
)

print(
    "Starting real-time order streaming..."
)


# ---------------------------------
# Send orders to Kafka
# ---------------------------------

for _, order in orders.iterrows():

    event = {

        "order_id": int(
            order["order_id"]
        ),

        "customer_id": int(
            order["customer_id"]
        ),

        "product_id": int(
            order["product_id"]
        ),

        "quantity": int(
            order["quantity"]
        ),

        "order_date": str(
            order["order_date"]
        ),

        "order_status": str(
            order["order_status"]
        )
    }


    producer.send(
        TOPIC_NAME,
        value=event
    )


    print(
        "Sent:",
        event
    )


    # Simulate real-time events

    time.sleep(1)


producer.flush()

producer.close()

print(
    "Streaming completed."
)