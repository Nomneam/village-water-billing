from datetime import  datetime, timedelta
from jose import jwt
from jose.exceptions import JWTError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


SECRET_KEY = "041689c7abc9677ae9810bea62495d85269f1c1469286848a989127e0520f5b52faf4f0b83a28b9ef94b6cba6868790058638365ea2bc7932a0c6acfe47bf8000db1b4a1253f6816ba77214d946ecac1551041680fc0a589a5c65a79ed452e7d15e1d026433a8999a5397f9bff3603d7007ca3f582f8708dc34b14880ba53c798146746f808624f7bbe4cbaa22079206d86db25352ca0ff64be7200b"
ALGORITHM = "HS256"

ACCESS_EXPIRE_MINUTES = 30
REFRESH_EXPIRE_DAYS = 7


security = HTTPBearer()


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )

    return payload
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)