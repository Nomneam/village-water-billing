from fastapi import FastAPI
import secrets

# Import the login router
from app.api.login import router as login_router
from app.api.user_management import router as user_management_router
from app.api.code_village import router as code_village_router
from app.api.employee_management import router as employee_management_router

app = FastAPI()

# Include the login router
app.include_router(login_router)
# Include the village router
app.include_router(code_village_router)
# Include the user management router
app.include_router(user_management_router)
# Include the employee management router
app.include_router(employee_management_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)