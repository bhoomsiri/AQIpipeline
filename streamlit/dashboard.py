import streamlit as st
st.set_page_config(page_title="AQI Dashboard", layout="wide")

import pandas as pd
import psycopg2
from datetime import datetime

# ----------------------------
# Connect to PostgreSQL
# ----------------------------
def get_data(conn):
    query = """
        SELECT city, aqi, timestamp_utc
        FROM air_quality_data
        ORDER BY timestamp_utc DESC
    """
    df = pd.read_sql(query, conn)
    return df

# ----------------------------
# Streamlit Dashboard
# ----------------------------

st.title("🌫️ Real-time Air Quality (AQI) Dashboard")

# เชื่อมต่อ DB 1 ครั้ง
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="airflow",
    user="airflow",
    password="airflow"
)

# --- ค่าเฉลี่ยรายวัน ---
query_avg_daily = """
    SELECT
      DATE(timestamp_utc) AS date,
      AVG(aqi)::int AS avg_aqi
    FROM air_quality_data
    WHERE timestamp_utc >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY date
    ORDER BY date;
"""
df_avg_daily = pd.read_sql(query_avg_daily, conn)
st.subheader("📊 ค่า AQI เฉลี่ยรายวัน (7 วันล่าสุดทั้ง 5 จังหวัด)")
st.line_chart(df_avg_daily.set_index("date"))

# --- Top AQI of this week ---
query_top_week = """
    SELECT
      city,
      MAX(aqi) AS max_aqi
    FROM air_quality_data
    WHERE timestamp_utc >= DATE_TRUNC('week', CURRENT_DATE)
    GROUP BY city
    ORDER BY max_aqi DESC
    LIMIT 5;
"""
df_top_week = pd.read_sql(query_top_week, conn)
st.subheader("🔥 เมืองที่มี AQI สูงสุดในสัปดาห์นี้")
st.bar_chart(df_top_week.set_index("city")["max_aqi"])

# --- ดึงข้อมูลทั้งหมดเพื่อกรอง ---
df = get_data(conn)

if df.empty:
    st.warning("ยังไม่มีข้อมูลในฐานข้อมูล")
else:
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

    # 🎛 ตัวกรอง
    min_date = df["timestamp_utc"].min().date()
    max_date = df["timestamp_utc"].max().date()

    st.sidebar.header("🔍 ตัวกรองข้อมูล")
    selected_date = st.sidebar.date_input("เลือกวัน", max_date, min_value=min_date, max_value=max_date)

    all_cities = df["city"].unique().tolist()
    selected_cities = st.sidebar.multiselect("เลือกเมือง", all_cities, default=all_cities)

    # 🧮 กรองข้อมูล
    filtered_df = df[
        (df["city"].isin(selected_cities)) &
        (df["timestamp_utc"].dt.date == selected_date)
    ].sort_values("timestamp_utc")

    st.subheader(f"📋 ข้อมูล AQI วันที่ {selected_date.strftime('%Y-%m-%d')}")
    st.dataframe(filtered_df, use_container_width=True)

    # 📈 แสดงกราฟแยกตามเมือง
    if not filtered_df.empty:
        for city in selected_cities:
            city_df = filtered_df[filtered_df["city"] == city]
            st.line_chart(
                data=city_df.set_index("timestamp_utc")[["aqi"]],
                use_container_width=True,
                height=300
            )
    else:
        st.info("ไม่มีข้อมูลสำหรับเงื่อนไขที่เลือก")
        
# 📌 ดึงข้อมูลย้อนหลัง 7 วัน
query = """
    SELECT city, aqi, timestamp_utc
    FROM air_quality_data
    WHERE timestamp_utc >= NOW() - INTERVAL '7 days'
    ORDER BY timestamp_utc ASC;
"""
df = pd.read_sql(query, conn)
conn.close()

# 📌 แปลง timestamp
df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])

# 🧠 ให้ user เลือก 2 เมือง
cities = df["city"].unique().tolist()

st.subheader("📈 เปรียบเทียบคุณภาพอากาศระหว่าง 2 เมือง")

col1, col2 = st.columns(2)
with col1:
    city1 = st.selectbox("เลือกเมืองที่ 1", cities)
with col2:
    city2 = st.selectbox("เลือกเมืองที่ 2", [c for c in cities if c != city1])

# 📊 กรองข้อมูล 2 เมือง
filtered_df = df[df["city"].isin([city1, city2])]

# ✅ Pivot เพื่อเตรียม line chart เปรียบเทียบ
pivot_df = filtered_df.pivot_table(
    index="timestamp_utc",
    columns="city",
    values="aqi"
).dropna()

# 🎨 แสดง line chart
st.line_chart(pivot_df, use_container_width=True)


st.subheader("📊 การเปลี่ยนแปลง AQI: วันนี้ vs เมื่อวาน")

query_day_compare = """
WITH today AS (
  SELECT city, AVG(aqi)::NUMERIC AS avg_aqi
  FROM air_quality_data
  WHERE DATE(timestamp_utc) = CURRENT_DATE
  GROUP BY city
),
yesterday AS (
  SELECT city, AVG(aqi)::NUMERIC AS avg_aqi
  FROM air_quality_data
  WHERE DATE(timestamp_utc) = CURRENT_DATE - INTERVAL '1 day'
  GROUP BY city
)
SELECT
  today.city,
  ROUND(today.avg_aqi, 1) AS today_avg,
  ROUND(yesterday.avg_aqi, 1) AS yesterday_avg,
  ROUND((today.avg_aqi - yesterday.avg_aqi) * 100.0 / NULLIF(yesterday.avg_aqi, 0), 1) AS percent_change
FROM today
JOIN yesterday ON today.city = yesterday.city
ORDER BY percent_change DESC;
"""

# ดึงจาก Postgres
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="airflow",
    user="airflow",
    password="airflow"
)
df_day_compare = pd.read_sql(query_day_compare, conn)
conn.close()

# ตกแต่ง emoji
def format_day_change(p):
    if p > 0:
        return f"🔺 +{p}%"
    elif p < 0:
        return f"🟢 {p}%"
    else:
        return "–"

df_day_compare["trend"] = df_day_compare["percent_change"].apply(format_day_change)

# แสดงผล
st.dataframe(
    df_day_compare[["city", "yesterday_avg", "today_avg", "trend"]],
    use_container_width=True
)



# ปิดการเชื่อมต่อ
conn.close()
