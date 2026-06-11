from fastapi import APIRouter, HTTPException ,Depends , Query ,status
from app.core.database import get_db_connection
from app.core.jwt import get_current_user
from app.schemas.basemodel_usermanagement import UserResponse, UserListResponse, HouseResponse ,UserCreate , UserPaginationResponse


router = APIRouter()


# แสดงข้อมูลลูบ้าน
@router.get(
    "/users",
    response_model=UserPaginationResponse
)
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
        cursor.execute(
            "SELECT COUNT(*) AS total FROM users"
        )
        total = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT
                user_id,
                line_user_id,
                full_name,
                phone,
                email
            FROM users
            ORDER BY user_id DESC
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



# เพิ่มผู้ใช้ใหม่ (ลูกบ้าน)
@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") not in ["SUPER_ADMIN", "STAFF"]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ตรวจสอบ email ซ้ำ
        if user.email:
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (user.email,)
            )

            if cursor.fetchone():
                raise HTTPException(
                    status_code=409,
                    detail="Email already exists"
                )

        # ตรวจสอบ LINE User ID ซ้ำ
        if user.line_user_id:
            cursor.execute(
                "SELECT user_id FROM users WHERE line_user_id = %s",
                (user.line_user_id,)
            )

            if cursor.fetchone():
                raise HTTPException(
                    status_code=409,
                    detail="LINE User ID already exists"
                )

        cursor.execute("""
            INSERT INTO users (
                line_user_id,
                full_name,
                phone,
                email
            )
            VALUES (%s, %s, %s, %s)
        """, (
            user.line_user_id,
            user.full_name,
            user.phone,
            user.email
        ))

        conn.commit()

        return {
            "message": "User created successfully",
            "user_id": cursor.lastrowid
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        cursor.close()
        conn.close()