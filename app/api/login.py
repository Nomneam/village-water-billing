from fastapi import APIRouter, HTTPException
from app.core.database import get_db_connection
from app.core.security import verify_password
from app.core.jwt import create_access_token ,create_refresh_token
from app.schemas.basemodel_login import Login, LoginResponse , RefreshRequest
from jose import JWTError, jwt
from app.core.jwt import SECRET_KEY, ALGORITHM
import pymysql

router = APIRouter()

# Login endpoint
@router.post("/login", response_model=LoginResponse)
async def login(login_data: Login):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute(
            """
            SELECT emp_id, username, password_hash, role, full_name
            FROM employees
            WHERE username = %s
            """,
            (login_data.username,)
        )

        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        if not verify_password(login_data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        payload = {
            "emp_id": user["emp_id"],
            "sub": user["username"],
            "role": user["role"]
        }

        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)

        return LoginResponse(
            message="Login successful",
            role=user["role"],
            full_name=user["full_name"],
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()

# Refresh token endpoint
@router.post("/refresh")
async def refresh_token(data: RefreshRequest):
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        new_access_token = create_access_token({
            "emp_id": payload["emp_id"],
            "sub": payload["sub"],
            "role": payload["role"]
        })

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")