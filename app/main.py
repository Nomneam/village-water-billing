from fastapi import FastAPI
import secrets

# Import the login router
from app.api.login import router as login_router

app = FastAPI()

# Include the login router
app.include_router(login_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)