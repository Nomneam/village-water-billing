from fastapi import APIRouter, HTTPException ,Depends , Query ,status
from app.core.database import get_db_connection
from app.core.jwt import get_current_user

router = APIRouter()

# แสดงข้อมูลพนักงาน
@router.get("/employees")
async def get_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    # permission
    if current_user.get("role") != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # count
        cursor.execute("SELECT COUNT(*) AS total FROM employees")
        total = cursor.fetchone()["total"]

        # data + join profile
        cursor.execute("""
            SELECT
                e.emp_id,
                e.username,
                e.full_name,
                e.role,

                p.employee_code,
                p.phone,
                p.email,
                p.address,
                p.profile_image,
                p.status AS profile_status,

                e.created_at,
                e.updated_at
            FROM employees e
            LEFT JOIN employee_profiles p
                ON e.emp_id = p.employee_id
            ORDER BY e.emp_id DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))

        employees = cursor.fetchall()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "employees": employees
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching employees: {str(e)}"
        )

    finally:
        cursor.close()
        conn.close()