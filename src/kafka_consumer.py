import json
import os

from kafka import KafkaConsumer
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


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
# PostgreSQL connection
# ---------------------------------

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL
)


# ---------------------------------
# Kafka configuration
# ---------------------------------

KAFKA_SERVER = "localhost:9092"

TOPIC_NAME = "ecommerce_orders"


# ---------------------------------
# Kafka consumer
# ---------------------------------

consumer = KafkaConsumer(

    TOPIC_NAME,

    bootstrap_servers=KAFKA_SERVER,

    auto_offset_reset="earliest",

    enable_auto_commit=True,

    group_id="ecommerce-db-consumer",

    value_deserializer=lambda value:
        json.loads(
            value.decode("utf-8")
        )
)


print(
    "Kafka → PostgreSQL consumer started..."
)


# ---------------------------------
# Process messages
# ---------------------------------

for message in consumer:

    order = message.value

    print(
        f"Received order "
        f"{order['order_id']}"
    )


    query = text(
        """
        INSERT INTO realtime_orders (
            order_id,
            customer_id,
            product_id,
            quantity,
            order_date,
            order_status
        )
        VALUES (
            :order_id,
            :customer_id,
            :product_id,
            :quantity,
            :order_date,
            :order_status
        )
        ON CONFLICT (order_id)
        DO NOTHING
        """
    )


    try:

        with engine.begin() as connection:

            connection.execute(
                query,
                {
                    "order_id":
                        order["order_id"],

                    "customer_id":
                        order["customer_id"],

                    "product_id":
                        order["product_id"],

                    "quantity":
                        order["quantity"],

                    "order_date":
                        order["order_date"],

                    "order_status":
                        order["order_status"]
                }
            )


        print(
            f"Order {order['order_id']} "
            f"inserted into PostgreSQL."
        )


    except Exception as error:

        print(
            f"Error processing order "
            f"{order['order_id']}: {error}"
        )