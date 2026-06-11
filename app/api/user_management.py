from fastapi import APIRouter, HTTPException ,Depends , Query
from app.core.database import get_db_connection
from app.core.jwt import get_current_user


router = APIRouter()


# แสดงข้อมูลลูบ้าน
@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ["SUPER_ADMIN", "STAFF"]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # จำนวนข้อมูลทั้งหมด
        cursor.execute("SELECT COUNT(*) AS total FROM users")
        total = cursor.fetchone()["total"]

        # ดึงข้อมูลตามหน้า
        cursor.execute("""
            SELECT full_name, phone, email
            FROM users
            LIMIT %s OFFSET %s
        """, (limit, offset))

        users = cursor.fetchall()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "users": users
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        cursor.close()
        conn.close()




