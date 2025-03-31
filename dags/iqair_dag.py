from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import logging

# ตั้งค่าเบื้องต้น
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# ตั้งค่า DAG
with DAG(
    dag_id='iqair_api_example',
    default_args=default_args,
    description='ดึงข้อมูลคุณภาพอากาศจาก IQAir API',
    schedule_interval='@hourly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['api', 'iqair'],
) as dag:

    def fetch_iqair_data():
        API_KEY = '4fb76e79-4433-4b76-9866-f8fdf19a9d33'  # 👈 เปลี่ยนเป็น API KEY จริงของคุณ
        CITY = 'Bangkok'
        STATE = 'Bangkok'
        COUNTRY = 'Thailand'
        url = f"http://api.airvisual.com/v2/city?city={CITY}&state={STATE}&country={COUNTRY}&key={API_KEY}"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            aqi = data['data']['current']['pollution']['aqius']
            logging.info(f"AQI in {CITY}: {aqi}")
        else:
            logging.warning(f"API call failed with status: {response.status_code}")

    fetch_task = PythonOperator(
        task_id='fetch_iqair_data',
        python_callable=fetch_iqair_data
    )
