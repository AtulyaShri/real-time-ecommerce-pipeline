
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="ecommerce_etl_pipeline",
    default_args=default_args,
    description="Validate and profile e-commerce datasets",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["ecommerce", "data-engineering"],
) as dag:

    validate_data = BashOperator(
        task_id="validate_data",
        bash_command=(
            "cd /opt/airflow/project && "
            "python src/validate_data.py"
        ),
    )

    profile_data = BashOperator(
        task_id="profile_data",
        bash_command=(
            "cd /opt/airflow/project && "
            "python src/data_profile.py"
        ),
    )

    validate_data >> profile_data
