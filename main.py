from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from api import admin_router, auth_router, history_router, summary_router, subscription_router, note_router
from config.origins_settings import origins_settings
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
app.include_router(subscription_router)

app.include_router(note_router)

origins = origins_settings.ALLOWED_ORIGINS.split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
