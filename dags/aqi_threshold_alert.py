from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import logging

THRESHOLD = 150  # ✅ ค่า AQI ที่จะเตือนถ้าเกิน

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def check_high_aqi():
    hook = PostgresHook(postgres_conn_id='postgres_conn')
    conn = hook.get_conn()
    cur = conn.cursor()

    # ✅ ตรวจข้อมูล 1 ชั่วโมงล่าสุดที่เกินค่ากำหนด
    cur.execute("""
        SELECT city, aqi, timestamp_utc
        FROM air_quality_data
        WHERE timestamp_utc >= NOW() - INTERVAL '1 hour'
          AND aqi >= %s
        ORDER BY aqi DESC;
    """, (THRESHOLD,))
    results = cur.fetchall()

    cur.close()
    conn.close()

    if results:
        logging.warning("🚨 พบเมืองที่ AQI เกินค่ากำหนดในชั่วโมงล่าสุด:")
        for city, aqi, timestamp in results:
            logging.warning(f"⚠️ {city} | AQI = {aqi} @ {timestamp}")
        raise ValueError("❌ พบค่าคุณภาพอากาศเกินกำหนดในบางเมือง")
    else:
        logging.info("✅ AQI ทุกเมืองอยู่ในเกณฑ์ปกติ")

with DAG(
    dag_id='aqi_threshold_alert',
    default_args=default_args,
    description='ตรวจสอบและแจ้งเตือน AQI สูงเกินค่ากำหนด',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # 🔄 Trigger จาก DAG อื่นเท่านั้น
    catchup=False,
    tags=['capstone', 'alert', 'aqi'],
) as dag:

    alert_task = PythonOperator(
        task_id='check_aqi_threshold',
        python_callable=check_high_aqi
    )
