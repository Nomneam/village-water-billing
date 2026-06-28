from fastapi import APIRouter, HTTPException, Depends, Query, status , Body
from app.core.database import get_db_connection
from app.core.jwt import get_current_user
from app.schemas.basemodel_village import VillageCreate ,VillageUpdate ,PasswordConfirm
from app.services.confirmpassword import confirm_super_admin_password
import pymysql

router = APIRouter()

# แสดงข้อมูลหมู่บ้านทั้งหมด
@router.get("/villages")
async def get_villages(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ["SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # นับจำนวนหมู่บ้านทั้งหมด
        cursor.execute(
            "SELECT COUNT(*) AS total FROM villages"
        )

        total = cursor.fetchone()["total"]

        # ดึงข้อมูลหมู่บ้าน
        cursor.execute("""
            SELECT
                village_id,
                village_code,
                village_name
            FROM villages
            ORDER BY village_id DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))

        villages = cursor.fetchall()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "villages": villages
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

    finally:
        cursor.close()
        conn.close()

# สร้างหมู่บ้านใหม่
@router.post("/villages/create", status_code=status.HTTP_201_CREATED)
async def create_village(
    village: VillageCreate = Body(...),
    password_confirm: PasswordConfirm = Body(...),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ยืนยันรหัสผ่าน
        confirm_super_admin_password(
            cursor=cursor,
            emp_id=current_user["emp_id"],
            password=password_confirm.password
        )

        cursor.execute("""
            INSERT INTO villages (
                village_code,
                village_name,
                created_at,
                updated_at
            )
            VALUES (%s, %s, NOW(), NOW())
        """, (
            "TEMP",
            village.village_name
        ))

        village_id = cursor.lastrowid
        village_code = f"M{village_id:02d}"

        cursor.execute("""
            UPDATE villages
            SET village_code = %s,
                updated_at = NOW()
            WHERE village_id = %s
        """, (
            village_code,
            village_id
        ))

        conn.commit()

        return {
            "message": "Village created successfully",
            "village_id": village_id,
            "village_code": village_code
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        print(e)

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        cursor.close()
        conn.close()

# แก้ไขข้อมูลหมู่บ้าน
@router.put("/villages/update/{village_id}")
async def update_village(
    village_id: int,
    village: VillageUpdate = Body(...),
    password_confirm: PasswordConfirm = Body(...),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ยืนยันรหัสผ่าน
        confirm_super_admin_password(
            cursor=cursor,
            emp_id=current_user["emp_id"],
            password=password_confirm.password
        )

        # ดึงข้อมูลเดิม
        cursor.execute("""
            SELECT village_name
            FROM villages
            WHERE village_id = %s
        """, (village_id,))

        existing = cursor.fetchone()

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail="Village not found"
            )

        # ใช้ค่าเดิมถ้าไม่ได้ส่งมา
        updated_name = (
            village.village_name
            if village.village_name is not None
            else existing["village_name"]
        )

        # อัปเดตข้อมูล
        cursor.execute("""
            UPDATE villages
            SET
                village_name = %s,
                updated_at = NOW()
            WHERE village_id = %s
        """, (
            updated_name,
            village_id
        ))

        conn.commit()

        return {
            "message": "Village updated successfully",
            "village_id": village_id
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        print(e)

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        cursor.close()
        conn.close()


# ดรอปดาวหมู่บ้าน (ใช้ใน select option)
@router.get("/villages/dropdown")
async def get_village_dropdown(
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ["SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                village_id,
                village_name
            FROM villages
            ORDER BY village_name ASC
        """)

        villages = cursor.fetchall()

        return {
            "villages": villages
        }

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        cursor.close()
        conn.close()



# ลบหมู่บ้าน
@router.delete("/villages/delete/{village_id}")
async def delete_village(
    village_id: int,
    password_confirm: PasswordConfirm,
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "SUPER_ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ยืนยันรหัสผ่าน
        confirm_super_admin_password(
            cursor=cursor,
            emp_id=current_user["emp_id"],
            password=password_confirm.password
        )

        # ตรวจสอบว่ามีหมู่บ้านหรือไม่
        cursor.execute(
            """
            SELECT village_id
            FROM villages
            WHERE village_id = %s
            """,
            (village_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Village not found"
            )

        # ตรวจสอบว่ามีบ้านในหมู่บ้านนี้หรือไม่
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM houses
            WHERE village_id = %s
            """,
            (village_id,)
        )

        house_count = cursor.fetchone()["total"]

        if house_count > 0:
            raise HTTPException(
                status_code=409,
                detail="Cannot delete village because it has houses"
            )

        # ลบหมู่บ้าน
        cursor.execute(
            """
            DELETE FROM villages
            WHERE village_id = %s
            """,
            (village_id,)
        )

        conn.commit()

        return {
            "message": "Village deleted successfully"
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        print(e)

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        cursor.close()
        conn.close()