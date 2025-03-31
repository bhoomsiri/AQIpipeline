# 🌫️ AQI Data Pipeline (Capstone Project BD533)

โปรเจกต์นี้ใช้ Apache Airflow, PostgreSQL และ Streamlit ในการสร้างระบบ pipeline สำหรับดึง วิเคราะห์ และแสดงผลข้อมูลคุณภาพอากาศ (AQI) จาก IQAir API

## 🧱 โครงสร้าง

- `dags/` – Airflow DAGs
- `dashboard/` – Streamlit Dashboard
- `docker-compose.yaml` – สำหรับรันระบบทั้งหมด
- `.env` – เก็บ API Key (ไม่ควร push ขึ้น GitHub)
- `requirements.txt` – Python packages

## 🚀 การใช้งาน

```bash
1. Clone โปรเจกต์จาก GitHub
git clone https://github.com/bhoomsiri/AQIpipeline.git
cd AQIpipeline

2. ติดตั้ง dependency ที่จำเป็น (เช่น streamlit, psycopg2, pandas)
pip install -r requirements.txt

3. รัน Dashboard
streamlit run dashboard.py --server.address=0.0.0.0 --server.port=8501

