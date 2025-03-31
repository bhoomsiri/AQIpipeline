from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from pytz import timezone
import requests
import logging
import time  # เพิ่มตรงนี้

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='fetch_aqi_multiple_cities',
    default_args=default_args,
    description='Fetch AQI for multiple cities and insert into PostgreSQL',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@hourly',
    catchup=False,
    tags=['capstone','bd533','aqi', 'multi-city'],
) as dag:

    def fetch_and_insert_multiple():
        API_KEY = '4fb76e79-4433-4b76-9866-f8fdf19a9d33'
        hook = PostgresHook(postgres_conn_id='postgres_conn')
        thai_tz = timezone('Asia/Bangkok')
        timestamp = datetime.now(thai_tz)

        cities = [
            {"city": "Bangkok", "state": "Bangkok", "country": "Thailand"},
            {"city": "Chiang Mai", "state": "Chiang Mai", "country": "Thailand"},
            {"city": "Ratchaburi", "state": "Ratchaburi", "country": "Thailand"},
            {"city": "Rua Yai", "state": "Suphan Buri", "country": "Thailand"},
            {"city": "Mueang Nonthaburi", "state": "Nonthaburi", "country": "Thailand"},
        ]

        for location in cities:
            city = location["city"]
            state = location["state"]
            country = location["country"]
            url = f"http://api.airvisual.com/v2/city?city={city}&state={state}&country={country}&key={API_KEY}"

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    aqi = data['data']['current']['pollution']['aqius']
                    logging.info(f"✅ {city}: AQI = {aqi}")

                    sql = """
                        INSERT INTO air_quality_data (city, aqi, timestamp_utc)
                        VALUES (%s, %s, %s);
                    """
                    hook.run(sql, parameters=(city, aqi, timestamp))

                else:
                    logging.warning(f"❌ API error for {city}: {response.status_code}")
            except Exception as e:
                logging.error(f"⚠️ Error fetching data for {city}: {e}")

            # ✅ หน่วงเวลาระหว่าง request
            time.sleep(15)  # 2 วินาทีต่อเมือง (ปรับได้)

    fetch_task = PythonOperator(
        task_id='fetch_aqi_all_cities',
        python_callable=fetch_and_insert_multiple
    )
