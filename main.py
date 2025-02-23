from fastapi import FastAPI
from sqlmodel import select

from api import admin_router, auth_router, demo_router, download_router, history_router, pdf_router, summarize_router, summary_router
from api.user.user import User
from db.config import create_db_and_tables, SessionDep

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root(session: SessionDep):
    return session.exec(select(User))

app.include_router(demo_router, prefix="/milestone_1")
app.include_router(pdf_router)
app.include_router(summarize_router)
app.include_router(summary_router)
app.include_router(download_router)
app.include_router(history_router)
app.include_router(auth_router)
app.include_router(admin_router)
