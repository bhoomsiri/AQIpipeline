from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime

def test_postgres_conn():
    hook = PostgresHook(postgres_conn_id="postgres_conn")  # 👈 ใช้ชื่อ conn ที่คุณตั้งไว้
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    result = cursor.fetchone()
    print(f"✅ PostgreSQL connected! Server version: {result[0]}")

with DAG(
    dag_id="test_postgres_conn_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=['capstone','bd533',"test", "postgres"]
) as dag:

    task = PythonOperator(
        task_id="check_postgres_connection",
        python_callable=test_postgres_conn
    )
