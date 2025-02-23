import pymupdf
from fastapi import APIRouter, UploadFile
from google import genai
from openai import OpenAI

from config import app_settings

gemini_client = genai.Client(api_key=app_settings.gemini_key)

router = APIRouter()

@router.post("/gemini")
def summarize_openai(file: UploadFile):
    with pymupdf.open(stream=file.file.read(), filetype="pdf") as doc:
        text = chr(12).join([page.get_text() for page in doc])
    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash", contents=f"Summarize the following article {text}"
    )
    text = response.text
    return {"summary": text}
