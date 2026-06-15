
# utils.py สร้างรหัสพนักงานอัตโนมัติ (employee_code)
def generate_employee_code(cursor):
    cursor.execute("""
        SELECT MAX(CAST(SUBSTRING(employee_code, 4) AS UNSIGNED)) AS max_no
        FROM employee_profiles
        WHERE employee_code IS NOT NULL
    """)

    result = cursor.fetchone()
    max_no = result["max_no"]

    if max_no is None:
        return "EMP0001"

    return f"EMP{max_no + 1:04d}"