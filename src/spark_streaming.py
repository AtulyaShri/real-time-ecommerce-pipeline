
import os
from dotenv import load_dotenv

load_dotenv()
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    current_timestamp,
)
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType,
    TimestampType,
    DoubleType,
)


# 1. Read database settings from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ecommerce_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not DB_PASSWORD:
    raise ValueError(
        "DB_PASSWORD is missing. Load your .env settings first."
    )


# 2. Start Spark
spark = (
    SparkSession.builder
    .appName("EcommerceKafkaStreaming")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# 3. Define the structure of Kafka order messages
order_schema = StructType([
    StructField("order_id", IntegerType(), True),
    StructField("customer_id", IntegerType(), True),
    StructField("product_id", IntegerType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("order_date", StringType(), True),
    StructField("order_status", StringType(), True),
])


# 4. Load product prices from the existing CSV file
products_path = "data/products.csv"

products = (
    spark.read
    .option("header", True)
    .csv(products_path)
    .select(
        col("product_id").cast("int"),
        col("price").cast("double").alias("unit_price"),
    )
)

# 5. Read the Kafka topic as a stream
orders_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "ecommerce_orders")
    .option("startingOffsets", "earliest")
    .load()
)

# 6. Convert Kafka JSON messages into structured columns
parsed_orders = (
    orders_stream
    .select(
        from_json(
            col("value").cast("string"),
            order_schema,
        ).alias("order")
    )
    .select("order.*")
    .withColumn(
        "order_date",
        col("order_date").cast(TimestampType()),
    )
)

# 7. Keep valid orders and enrich them with product prices
valid_orders = parsed_orders.filter(
    col("order_id").isNotNull()
    & col("customer_id").isNotNull()
    & col("product_id").isNotNull()
    & (col("quantity") > 0)
)

enriched_orders = (
    valid_orders
    .join(products, on="product_id", how="inner")
    .withColumn(
        "order_value",
        (col("quantity") * col("unit_price")).cast("double"),
    )
    .withColumn("processed_at", current_timestamp())
)


# 8. Write each Spark micro-batch to PostgreSQL

def save_to_postgres(batch_df, batch_id):
    if batch_df.isEmpty():
        return

    jdbc_url = (
        f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    output_df = batch_df.select(
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "order_date",
        "order_status",
        "unit_price",
        "order_value",
        "processed_at",
    )

    # Collect this micro-batch and use PostgreSQL upserts.
    # Suitable for this small learning project.
    rows = output_df.collect()

    from sqlalchemy import create_engine, text
    from datetime import datetime

    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    upsert_sql = text("""
        INSERT INTO spark_processed_orders (
            order_id, customer_id, product_id, quantity,
            order_date, order_status, unit_price,
            order_value, processed_at
        )
        VALUES (
            :order_id, :customer_id, :product_id, :quantity,
            :order_date, :order_status, :unit_price,
            :order_value, :processed_at
        )
        ON CONFLICT (order_id) DO UPDATE SET
            order_status = EXCLUDED.order_status,
            order_value = EXCLUDED.order_value,
            processed_at = EXCLUDED.processed_at
    """)

    with engine.begin() as connection:
        for row in rows:
            connection.execute(upsert_sql, row.asDict())

    engine.dispose()
    print(f"Saved batch {batch_id}: {len(rows)} orders")


    # Upsert prevents duplicate order IDs when a batch is replayed.
    output_df.createOrReplaceTempView("current_batch")

    batch_df.sparkSession.sql("""
        SELECT * FROM current_batch
    """).write.jdbc(
        url=jdbc_url,
        table="spark_processed_orders_staging",
        mode="append",
        properties={
            "user": DB_USER,
            "password": DB_PASSWORD,
            "driver": "org.postgresql.Driver",
        },
    )

    print(f"Processed Spark batch: {batch_id}")


# 9. Start streaming
query = (
    enriched_orders.writeStream
    .foreachBatch(save_to_postgres)
    .option(
        "checkpointLocation",
        "checkpoints/spark_ecommerce_orders",
    )
    .trigger(processingTime="10 seconds")
    .start()
)

query.awaitTermination()
