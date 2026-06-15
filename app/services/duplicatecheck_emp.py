from fastapi import  HTTPException



def check_employee_duplicate(cursor, username: str, email: str, phone: str):
    # check username
    cursor.execute("""
        SELECT emp_id FROM employees WHERE username = %s
    """, (username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username already exists")

    # check email
    cursor.execute("""
        SELECT employee_id FROM employee_profiles WHERE email = %s
    """, (email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already exists")

    # check phone
    cursor.execute("""
        SELECT employee_id FROM employee_profiles WHERE phone = %s
    """, (phone,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Phone already exists")