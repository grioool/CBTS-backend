import uvicorn
from fastapi import FastAPI

from api import demo_router
from api import pdf_router
from api import summarize_router
from api import summary_router
from api import download_router
from api import history_router
from api import auth_router
from api import admin_router

app = FastAPI()
app.include_router(demo_router, prefix="/milestone_1")
app.include_router(pdf_router)
app.include_router(summarize_router)
app.include_router(summary_router)
app.include_router(download_router)
app.include_router(history_router)
app.include_router(auth_router)
app.include_router(admin_router)