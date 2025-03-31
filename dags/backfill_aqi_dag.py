from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from pytz import timezone
import requests
import time
import logging

# ============ ตั้งค่าหลัก ============
API_KEY = '4fb76e79-4433-4b76-9866-f8fdf19a9d33'
HOURS_BACK = 12  # <<< ดึงย้อนหลังกี่ชั่วโมง

CITIES = [
    {"city": "Bangkok", "state": "Bangkok", "country": "Thailand"},
    {"city": "Chiang Mai", "state": "Chiang Mai", "country": "Thailand"},
    {"city": "Ratchaburi", "state": "Ratchaburi", "country": "Thailand"},
    {"city": "Rua Yai", "state": "Suphan Buri", "country": "Thailand"},
    {"city": "Mueang Nonthaburi", "state": "Nonthaburi", "country": "Thailand"},
]

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# ============ ฟังก์ชันหลัก ============
def backfill_aqi():
    hook = PostgresHook(postgres_conn_id='postgres_conn')
    conn = hook.get_conn()
    cur = conn.cursor()
    thai_tz = timezone('Asia/Bangkok')
    now = datetime.now(thai_tz)

    for hour_delta in range(1, HOURS_BACK + 1):
        timestamp = now - timedelta(hours=hour_delta)
        timestamp = timestamp.replace(minute=0, second=0, microsecond=0)

        for loc in CITIES:
            city = loc["city"]
            state = loc["state"]
            country = loc["country"]

            url = f"http://api.airvisual.com/v2/city?city={city}&state={state}&country={country}&key={API_KEY}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    aqi = data['data']['current']['pollution']['aqius']

                    # ❗ Check if already exists
                    cur.execute(
                        "SELECT 1 FROM air_quality_data WHERE city=%s AND timestamp_utc=%s",
                        (city, timestamp)
                    )
                    if cur.fetchone() is None:
                        cur.execute(
                            "INSERT INTO air_quality_data (city, aqi, timestamp_utc) VALUES (%s, %s, %s)",
                            (city, aqi, timestamp)
                        )
                        conn.commit()
                        logging.info(f"✅ Inserted: {city} @ {timestamp} → AQI: {aqi}")
                    else:
                        logging.info(f"⏩ Skipped (already exists): {city} @ {timestamp}")
                else:
                    logging.warning(f"❌ API error {response.status_code} for {city}")
            except Exception as e:
                logging.error(f"⚠️ Error fetching data for {city}: {e}")

            time.sleep(5)  # <<< ป้องกัน rate limit

    cur.close()
    conn.close()
    logging.info("🎉 Backfill completed.")

# ============ สร้าง DAG ============
with DAG(
    dag_id='backfill_aqi_data',
    description='ดึงข้อมูล AQI ย้อนหลังตามชั่วโมงที่กำหนด',
    default_args=default_args,
    schedule_interval=None,  # รัน manual
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['capstone','bd533','aqi', 'backfill'],
) as dag:

    run_backfill = PythonOperator(
        task_id='run_backfill_aqi',
        python_callable=backfill_aqi
    )
