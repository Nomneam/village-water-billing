from fastapi import HTTPException


def check_duplicate_user_data(cursor, user, user_id: int = None):
    """
    ตรวจสอบข้อมูลซ้ำของ users

    user_id = None  -> ใช้ตอนสร้างข้อมูลใหม่
    user_id != None -> ใช้ตอนแก้ไขข้อมูล
    """

    fields = [
        ("citizen_id", user.citizen_id, "Citizen ID already exists"),
        ("email", user.email, "Email already exists"),
        ("line_user_id", user.line_user_id, "LINE User ID already exists"),
        ("phone", user.phone, "Phone number already exists"),
    ]

    for field_name, value, error_message in fields:
        # ข้ามถ้าเป็น None หรือค่าว่าง
        if not value:
            continue

        query = f"""
            SELECT user_id
            FROM users
            WHERE {field_name} = %s
        """

        params = [value]

        # ถ้าเป็น update ให้ข้าม user ตัวเอง
        if user_id is not None:
            query += " AND user_id != %s"
            params.append(user_id)

        cursor.execute(query, tuple(params))

        if cursor.fetchone():
            raise HTTPException(
                status_code=409,
                detail=error_message
            )