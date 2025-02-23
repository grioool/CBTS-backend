import uvicorn
from fastapi import FastAPI

from api import pdf_router

app = FastAPI()
app.include_router(pdf_router, prefix="/pdf")