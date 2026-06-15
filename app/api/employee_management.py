from fastapi import APIRouter, HTTPException ,Depends , Query ,status
from app.core.database import get_db_connection
from app.core.jwt import get_current_user
from app.core.security import hash_password
from app.schemas.basemoel_employee import EmployeeCreateRequest
from app.services.utils import generate_employee_code
import pymysql

router = APIRouter()

# แสดงข้อมูลพนักงาน
@router.get("/employees")
async def get_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # total
        cursor.execute("SELECT COUNT(*) AS total FROM employees")
        total = cursor.fetchone()["total"]

        # data
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
                p.status AS profile_status

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


# สร้างพนักงานใหม่
@router.post("/employees/create")
async def create_employee(
    data: EmployeeCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Permission denied")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. insert employee
        cursor.execute("""
            INSERT INTO employees (
                username,
                password_hash,
                full_name,
                role,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """, (
            data.username,
            hash_password(data.password),   
            data.full_name,
            data.role
        ))

        emp_id = cursor.lastrowid

        # 2. AUTO employee_code
        employee_code = generate_employee_code(cursor)

        # 3. insert profile
        cursor.execute("""
            INSERT INTO employee_profiles (
                employee_id,
                employee_code,
                phone,
                email,
                address,
                profile_image,
                status,
                created_at,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE', NOW(), NOW())
        """, (
            emp_id,
            employee_code,
            data.phone,
            data.email,
            data.address,
            data.profile_image
        ))

        conn.commit()

        return {
            "message": "Employee created successfully",
            "emp_id": emp_id,
            "employee_code": employee_code
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()