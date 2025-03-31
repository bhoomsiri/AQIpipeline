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

def aggregate_daily_avg():
    hook = PostgresHook(postgres_conn_id='postgres_conn')
    conn = hook.get_conn()
    cur = conn.cursor()

    try:
        # ✅ ลบข้อมูลของวันที่จะคำนวณก่อน (วันนี้)
        cur.execute("DELETE FROM aqi_daily_avg WHERE date = CURRENT_DATE;")

        # ✅ ดึงข้อมูลจาก air_quality_data แล้วคำนวณค่าเฉลี่ยรายวัน
        cur.execute("""
        INSERT INTO aqi_daily_avg (city, date, avg_aqi)
        SELECT
            city,
            date,
            ROUND(AVG(aqi))::int AS avg_aqi
        FROM (
            SELECT
                city,
                DATE(timestamp_utc) AS date,
                aqi
            FROM air_quality_data
            WHERE DATE(timestamp_utc) = CURRENT_DATE
        ) AS sub
        GROUP BY city, date;
        """)


        conn.commit()
        logging.info("✅ คำนวณและบันทึกค่า AQI เฉลี่ยรายวันเรียบร้อยแล้ว")
    except Exception as e:
        logging.error(f"❌ เกิดข้อผิดพลาด: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

with DAG(
    dag_id='aggregate_aqi_daily',
    default_args=default_args,
    schedule_interval='30 1 * * *',  # ทุกวัน 01:30
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['capstone', 'aggregate', 'aqi'],
) as dag:

    task = PythonOperator(
        task_id='compute_avg_aqi_daily',
        python_callable=aggregate_daily_avg
    )
