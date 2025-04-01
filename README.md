# AQI Data Pipeline 🌫️

โครงการนี้เป็นระบบ ETL Pipeline สำหรับดึงข้อมูลคุณภาพอากาศ (Air Quality Index - AQI) จาก [IQAir API](https://www.iqair.com/) มาจัดเก็บในฐานข้อมูลและแสดงผลผ่าน Dashboard โดยใช้เครื่องมือหลัก ได้แก่ Apache Airflow, PostgreSQL และ Streamlit ทั้งหมดถูกจัดการและรันผ่าน Docker Compose

---

## 📊 เทคโนโลยีที่ใช้

- **Apache Airflow** – สำหรับจัดการ ETL Workflow
- **PostgreSQL** – สำหรับจัดเก็บข้อมูล AQI
- **Streamlit** – สำหรับแสดง Dashboard แบบ interactive
- **Docker Compose** – สำหรับจัดการ service ทั้งหมดแบบง่าย

---

## 🚀 วิธีติดตั้งและใช้งานระบบ

### 1. Clone โปรเจกต์
```bash
git clone https://github.com/bhoomsiri/AQIpipeline.git
cd AQIpipeline
```

### 2. สร้างไฟล์ `.env` จากตัวอย่าง
```bash
cp .env.example .env
```
> แล้วใส่ API Key จาก IQAir ในไฟล์ `.env`

### 3. Initial Airflow (เฉพาะครั้งแรกเท่านั้น)
```bash
docker-compose run airflow-init
```

### 4. รันระบบทั้งหมด
```bash
docker-compose up
```

---

## 🔗 Web Interface ต่าง ๆ

| บริการ         | URL                    |
|----------------|-------------------------|
| Airflow UI     | http://localhost:8080  |
| Streamlit      | http://localhost:8501  |
| pgAdmin (ถ้ามี)| http://localhost:5050  |

---

## 📊 การทำงานของระบบ

1. DAG ของ Airflow จะดึงข้อมูล AQI ประจำวันจาก IQAir API
2. ข้อมูลถูกจัดเก็บไว้ใน PostgreSQL
3. Streamlit Dashboard ดึงข้อมูลจากฐานข้อมูลมาแสดงผลในรูปแบบ interactive

---

## 📸 ตัวอย่าง Dashboard

> *(แนะนำให้เพิ่ม screenshot ของหน้า dashboard ที่นี่)*

---

## 🙋️ ผู้จัดทำ

- Bhoomsiri (https://github.com/bhoomsiri)

---

## ⚠️ หมายเหตุ

- หากใช้งานบน Windows แนะนำให้ใช้ WSL2 หรือ Docker Desktop
- หากพบปัญหาในการติดตั้ง/ใช้งาน สามารถเปิด issue ใน GitHub Repository นี้
