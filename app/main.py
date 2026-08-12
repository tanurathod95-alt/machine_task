from fastapi import FastAPI
from sqlmodel import SQLModel
from sqlalchemy.exc import OperationalError
from app.database import engine,create_db_and_tables
from app.routers.auth_router import router as auth_router
from app.routers.student_router import router as student_router
app=FastAPI()


@app.on_event("startup")
def on_startup():

    create_db_and_tables()
    try:
        SQLModel.metadata.create_all(engine)
        print("Database Connected Successfully!")
    except OperationalError as e:
        print("Database Connection Failed:", e)

app.include_router(auth_router)

app.include_router(student_router)

@app.get("/")
def home():
    return {"message": "Taks API 1.0"}