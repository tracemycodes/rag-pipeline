from fastapi import FastAPI
from app.modules.users.users import router as users_router

app = FastAPI()

@app.get("/health")
def health_check():    return {"status": "healthy"}


app.include_router(users_router)