from fastapi import HTTPException
from app.core.security import verify_password

def confirm_super_admin_password(
    cursor,
    emp_id: int,
    password: str
):
    cursor.execute("""
        SELECT password_hash
        FROM employees
        WHERE emp_id = %s
    """, (emp_id,))

    employee = cursor.fetchone()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not verify_password(
        password,
        employee["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )