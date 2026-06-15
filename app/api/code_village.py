from fastapi import APIRouter, HTTPException, Depends, Query, status
from app.core.database import get_db_connection
from app.core.jwt import get_current_user
from app.schemas.basemodel_house import HouseCreate
import pymysql

router = APIRouter()

# แสดงข้อมูลลูบ้าน
@router.get("/village")
async def get_village(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ["SUPER_ADMIN", "STAFF"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # นับจำนวนบ้านทั้งหมด
        cursor.execute("SELECT COUNT(*) AS total FROM houses")
        total = cursor.fetchone()["total"]

        # ดึงข้อมูลบ้านพร้อมข้อมูลเจ้าของบ้าน
        cursor.execute("""
            SELECT
                h.house_id,
                h.house_no,
                h.address,
                h.status,
                h.user_id,
                u.full_name,
                u.phone,
                u.email
            FROM houses h
            LEFT JOIN users u
                ON h.user_id = u.user_id
            ORDER BY h.house_id DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))

        houses = cursor.fetchall()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "houses": houses
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    finally:
        cursor.close()
        conn.close()

        
# เพิ่มบ้านใหม่
@router.post("/village", status_code=status.HTTP_201_CREATED)
async def create_house(
    house: HouseCreate,
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ["SUPER_ADMIN", "STAFF"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ตรวจสอบ user_id
        cursor.execute(
            "SELECT user_id FROM users WHERE user_id = %s",
            (house.user_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # ตรวจสอบ village_id และดึง village_code
        cursor.execute("""
            SELECT village_code
            FROM villages
            WHERE village_id = %s
        """, (house.village_id,))

        village = cursor.fetchone()

        if village is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Village not found"
            )

        village_code = village["village_code"]

        # ตรวจสอบบ้านเลขที่ซ้ำในหมู่บ้านเดียวกัน
        cursor.execute("""
            SELECT house_id
            FROM houses
            WHERE village_id = %s
              AND house_no = %s
        """, (
            house.village_id,
            house.house_no
        ))

        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="House number already exists in this village"
            )

        # เพิ่มข้อมูลบ้าน (meter_number เป็น NULL ชั่วคราว)
        cursor.execute("""
            INSERT INTO houses (
                village_id,
                user_id,
                house_no,
                meter_number,
                address,
                status,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, NULL, %s, %s, NOW(), NOW())
        """, (
            house.village_id,
            house.user_id,
            house.house_no,
            house.address,
            house.status
        ))

        # รับ house_id ที่ถูกสร้าง
        house_id = cursor.lastrowid

        # สร้างเลขมิเตอร์
        meter_number = f"{village_code}-{house_id:06d}"

        # อัปเดตเลขมิเตอร์กลับเข้าไป
        cursor.execute("""
            UPDATE houses
            SET meter_number = %s
            WHERE house_id = %s
        """, (
            meter_number,
            house_id
        ))

        conn.commit()

        return {
            "message": "House created successfully",
            "house_id": house_id,
            "meter_number": meter_number
        }

    except HTTPException:
        conn.rollback()
        raise

    except pymysql.MySQLError:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    finally:
        cursor.close()
        conn.close()