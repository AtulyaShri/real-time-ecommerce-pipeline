
import os

import pandas as pd
import plotly.express as px
import streamlit as st

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# ----------------------------------------
# 1. Page configuration
# ----------------------------------------

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="",
    layout="wide",
)

load_dotenv()

st.title("E-Commerce Data Engineering Dashboard")
st.caption(
    "Business analytics powered by PostgreSQL, "
    "with Kafka and Spark streaming integration."
)


# ----------------------------------------
# 2. Database connection
# ----------------------------------------

required_vars = [
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
]

missing = [key for key in required_vars if not os.getenv(key)]

if missing:
    st.error(f"Missing database settings: {', '.join(missing)}")
    st.stop()

db_url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(db_url)


@st.cache_data(ttl=30)
def read_sql(query):
    with engine.connect() as connection:
        return pd.read_sql_query(text(query), connection)


# ----------------------------------------
# 3. Load dashboard datasets
# ----------------------------------------

try:
    orders = read_sql("""
        SELECT
            order_id,
            customer_id,
            product_id,
            quantity,
            order_date,
            order_status
        FROM orders
    """)

    products = read_sql("""
        SELECT
            product_id,
            product_name,
            category,
            price,
            stock_quantity
        FROM products
    """)

    payments = read_sql("""
        SELECT
            payment_id,
            order_id,
            payment_method,
            payment_status,
            amount,
            payment_date
        FROM payments
    """)

except Exception as error:
    st.error(
        "Could not load PostgreSQL data. "
        "Check your database connection and table names."
    )
    st.exception(error)
    st.stop()


if orders.empty:
    st.warning("The orders table is empty. Load data before using the dashboard.")
    st.stop()


# ----------------------------------------
# 4. Filters
# ----------------------------------------

orders["order_date"] = pd.to_datetime(
    orders["order_date"], errors="coerce"
)

orders["quantity"] = pd.to_numeric(
    orders["quantity"], errors="coerce"
).fillna(0)

products["price"] = pd.to_numeric(
    products["price"], errors="coerce"
)

payments["amount"] = pd.to_numeric(
    payments["amount"], errors="coerce"
)

orders["order_status"] = (
    orders["order_status"].fillna("Unknown")
)

valid_dates = orders["order_date"].dropna()

if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    start_date, end_date = st.sidebar.date_input(
        "Order date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    orders = orders[
        orders["order_date"].dt.date.between(
            start_date, end_date
        )
    ]

statuses = sorted(orders["order_status"].unique().tolist())

selected_statuses = st.sidebar.multiselect(
    "Order status",
    options=statuses,
    default=statuses,
)

orders = orders[
    orders["order_status"].isin(selected_statuses)
]


# ----------------------------------------
# 5. Prepare business metrics
# ----------------------------------------

product_lookup = products.set_index("product_id")["price"]

orders["unit_price"] = orders["product_id"].map(product_lookup)

orders["order_value"] = (
    orders["quantity"] * orders["unit_price"]
)

completed_payments = payments[
    payments["payment_status"].str.lower().eq("completed")
].copy()

# Revenue is based on successful payment records.
# Payment totals may differ from estimated order values.
paid_revenue = completed_payments["amount"].sum()

total_orders = orders["order_id"].nunique()
total_customers = orders["customer_id"].nunique()
total_products = products["product_id"].nunique()

avg_order_value = (
    orders.groupby("order_id")["order_value"].sum().mean()
    if total_orders
    else 0
)


# ----------------------------------------
# 6. KPI cards
# ----------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric("Orders", f"{total_orders:,}")
col2.metric("Customers", f"{total_customers:,}")
col3.metric("Products", f"{total_products:,}")
col4.metric("Completed payment value", f"₹{paid_revenue:,.2f}")

st.caption(
    "Completed payment value uses all completed payment records. "
    "It is not restricted by the order-date filter."
)

st.divider()


# ----------------------------------------
# 7. Order status and daily trends
# ----------------------------------------

left, right = st.columns(2)

with left:
    st.subheader("Orders by Status")

    status_df = (
        orders.groupby("order_status", as_index=False)
        .agg(total_orders=("order_id", "nunique"))
    )

    if not status_df.empty:
        fig = px.bar(
            status_df,
            x="order_status",
            y="total_orders",
            color="order_status",
            title="Order Status Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Daily Order Trend")

    daily_df = (
        orders.dropna(subset=["order_date"])
        .assign(order_day=lambda df: df["order_date"].dt.date)
        .groupby("order_day", as_index=False)
        .agg(total_orders=("order_id", "nunique"))
    )

    if not daily_df.empty:
        fig = px.line(
            daily_df,
            x="order_day",
            y="total_orders",
            markers=True,
            title="Orders Over Time",
        )
        st.plotly_chart(fig, use_container_width=True)


# ----------------------------------------
# 8. Product performance
# ----------------------------------------

st.subheader("Product Performance")

product_sales = (
    orders.groupby("product_id", as_index=False)
    .agg(
        units_sold=("quantity", "sum"),
        estimated_value=("order_value", "sum"),
    )
    .merge(products, on="product_id", how="left")
    .sort_values("units_sold", ascending=False)
)

if not product_sales.empty:
    fig = px.bar(
        product_sales.head(10),
        x="product_name",
        y="units_sold",
        title="Top 10 Products by Units Ordered",
        hover_data=["category", "estimated_value"],
    )
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(product_sales, use_container_width=True)


# ----------------------------------------
# 9. Payment analytics
# ----------------------------------------

st.subheader("Payment Status")

payment_summary = (
    payments.groupby("payment_status", as_index=False)
    .agg(
        payment_count=("payment_id", "nunique"),
        payment_value=("amount", "sum"),
    )
)

if not payment_summary.empty:
    fig = px.pie(
        payment_summary,
        names="payment_status",
        values="payment_count",
        title="Payments by Status",
    )
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(payment_summary, use_container_width=True)


# ----------------------------------------
# 10. Recent orders
# ----------------------------------------

st.subheader("Recent Orders")

recent_orders = (
    orders.merge(
        products[["product_id", "product_name"]],
        on="product_id",
        how="left",
    )
    .sort_values("order_date", ascending=False)
)

st.dataframe(
    recent_orders[
        [
            "order_id",
            "customer_id",
            "product_name",
            "quantity",
            "order_date",
            "order_status",
            "order_value",
        ]
    ].head(50),
    use_container_width=True,
)

if st.button("Refresh dashboard"):
    st.cache_data.clear()
    st.rerun()
