from fastapi import FastAPI, Response

from api import admin_router, auth_router, history_router, summary_router
from db.config import create_db_and_tables

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return Response()

app.include_router(summary_router)
app.include_router(history_router)
app.include_router(auth_router)
app.include_router(admin_router)
