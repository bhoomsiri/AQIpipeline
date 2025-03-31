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
git clone https://github.com/yourusername/aqi-pipeline.git
cd aqi-pipeline

cp .env.example .env  # แล้วใส่ API_KEY ของคุณ
docker-compose up
