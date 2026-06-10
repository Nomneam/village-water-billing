import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10
    )
# กัน DB ล่มเวลา traffic เยอะ ใน Project มีขนาดใหญ่ แนะนำใช้ Connection Pooling
# pool = PooledDB(
#     creator=pymysql,
#     maxconnections=20,     # สูงสุดที่รองรับพร้อมกัน
#     mincached=5,           # connection เริ่มต้น
#     maxcached=10,          # เก็บไว้ใช้ซ้ำ
#     blocking=True,         # ถ้าเต็ม -> รอ (กัน crash)
#     maxusage=1000,         # ใช้ซ้ำได้กี่ครั้งก่อน reset
#     ping=1,                # เช็ค connection ก่อนใช้
#     host=os.getenv("DB_HOST"),
#     port=int(os.getenv("DB_PORT", 3306)),
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD"),
#     database=os.getenv("DB_NAME"),
#     cursorclass=pymysql.cursors.DictCursor,
#     charset="utf8mb4"
# )

# def get_db_connection():
#     return pool.connection()