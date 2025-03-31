from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import logging

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def validate_and_clean_aqi_data():
    hook = PostgresHook(postgres_conn_id='postgres_conn')
    conn = hook.get_conn()
    cur = conn.cursor()

    errors = []

    # ✅ 1. ตรวจว่ามีข้อมูลล่าสุดใน 24 ชั่วโมง
    cur.execute("""
        SELECT COUNT(*) FROM air_quality_data
        WHERE timestamp_utc >= NOW() - INTERVAL '24 hours'
    """)
    count = cur.fetchone()[0]
    if count == 0:
        errors.append("❌ ไม่มีข้อมูลในช่วง 24 ชั่วโมงที่ผ่านมา")

    # ❗ 2. ตรวจสอบ AQI < 0
    cur.execute("SELECT COUNT(*) FROM air_quality_data WHERE aqi < 0")
    negative_count = cur.fetchone()[0]
    if negative_count > 0:
        errors.append(f"❌ พบ AQI ติดลบ: {negative_count} รายการ")

    # ⚠️ 3. ตรวจสอบและลบข้อมูลซ้ำ
    cur.execute("""
        WITH ranked AS (
            SELECT ctid, ROW_NUMBER() OVER (
                PARTITION BY city, timestamp_utc
                ORDER BY ctid
            ) AS rn
            FROM air_quality_data
        )
        DELETE FROM air_quality_data
        WHERE ctid IN (
            SELECT ctid FROM ranked WHERE rn > 1
        );
    """)
    deleted_rows = cur.rowcount
    if deleted_rows > 0:
        logging.warning(f"🧹 ลบข้อมูลซ้ำแล้ว {deleted_rows} แถว")

    cur.close()
    conn.commit()
    conn.close()

    if errors:
        for e in errors:
            logging.warning(e)
        raise ValueError("🛑 Data validation พบข้อผิดพลาด โปรดตรวจสอบ log.")
    else:
        logging.info("✅ Data validation ผ่านทั้งหมด และข้อมูลซ้ำถูกลบเรียบร้อยแล้ว")

with DAG(
    dag_id='validate_aqi_data',
    default_args=default_args,
    description='Validate and clean AQI data',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['capstone','bd533','aqi', 'validate', 'clean'],
) as dag:

    validate_task = PythonOperator(
        task_id='validate_and_clean',
        python_callable=validate_and_clean_aqi_data
    )