from pydantic import BaseModel

class Login(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    role: str
    full_name: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str