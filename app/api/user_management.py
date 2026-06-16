from fastapi import APIRouter, HTTPException ,Depends , Query ,status
from app.core.database import get_db_connection
from app.core.jwt import get_current_user
from app.schemas.basemodel_usermanagement import UserCreate , UserPaginationResponse ,UserUpdate
from app.services.user_validation import check_duplicate_user_data


router = APIRouter()


# แสดงข้อมูลลูบ้าน
@router.get("/users",response_model=UserPaginationResponse)
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
                citizen_id,
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
        # ตรวจสอบข้อมูลซ้ำ
        check_duplicate_user_data(cursor, user)

        # เพิ่มข้อมูล
        cursor.execute("""
            INSERT INTO users (
                citizen_id,
                line_user_id,
                full_name,
                phone,
                email,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            user.citizen_id,
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

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    finally:
        cursor.close()
        conn.close()



# แก้ไขข้อมูลผู้ใช้ (ลูกบ้าน)
@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user: UserUpdate,
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
        # ดึงข้อมูลเดิม
        cursor.execute("""
            SELECT
                citizen_id,
                line_user_id,
                full_name,
                phone,
                email
            FROM users
            WHERE user_id = %s
        """, (user_id,))

        existing_user = cursor.fetchone()

        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # รวมข้อมูลเดิมกับข้อมูลใหม่
        updated_data = {
            "citizen_id": (
                user.citizen_id
                if user.citizen_id is not None
                else existing_user["citizen_id"]
            ),
            "line_user_id": (
                user.line_user_id
                if user.line_user_id is not None
                else existing_user["line_user_id"]
            ),
            "full_name": (
                user.full_name
                if user.full_name is not None
                else existing_user["full_name"]
            ),
            "phone": (
                user.phone
                if user.phone is not None
                else existing_user["phone"]
            ),
            "email": (
                user.email
                if user.email is not None
                else existing_user["email"]
            ),
        }

        # ตรวจสอบข้อมูลซ้ำ
        check_duplicate_user_data(
            cursor=cursor,
            user=UserUpdate(**updated_data),
            user_id=user_id
        )

        # อัปเดตข้อมูล
        cursor.execute("""
            UPDATE users
            SET
                citizen_id = %s,
                line_user_id = %s,
                full_name = %s,
                phone = %s,
                email = %s,
                updated_at = NOW()
            WHERE user_id = %s
        """, (
            updated_data["citizen_id"],
            updated_data["line_user_id"],
            updated_data["full_name"],
            updated_data["phone"],
            updated_data["email"],
            user_id
        ))

        conn.commit()

        return {
            "message": "User updated successfully",
            "user_id": user_id
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