import hashlib
from datetime import datetime, timedelta
from typing import Annotated, Optional

import fitz
from fastapi import UploadFile, Depends, HTTPException
from google import genai
from google.cloud import storage
from sqlmodel import select

from api.auth.auth_service import AuthServiceDep
from api.summary.length import Length
from api.summary.style import Style
from api.summary.summary import Summary
from config import ai_settings
from config.storage_settings import storage_settings
from db.config import SessionDep


def get_gemini_client():
    return genai.Client(api_key=ai_settings.GEMINI_KEY)


def get_bucket():
    client = storage.Client()
    return client.bucket(storage_settings.STORAGE_NAME)


def generate_hash(filename: str, length: int = 10):
    return hashlib.sha256(filename.encode()).hexdigest()[:length]


def get_daily_limit_for_role(role_id: Optional[int]) -> int:
    return {2: 5, 3: 50, 4: 200}.get(role_id, 5)


class SummaryService:
    def __init__(self, session: SessionDep, auth_service: AuthServiceDep):
        self.session = session
        self.auth_service = auth_service

    def upload_text_to_gcs(self, text: str, destination_blob_name: str):
        bucket = get_bucket()
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(text, content_type="text/plain")
        return blob.public_url

    async def summarize_pdf(self, style: Style, length: Length, file: UploadFile, token: str):
        user = await self.auth_service.get_current_user(token)

        if (
            user.counter_last_update is None
            or (datetime.now() - user.counter_last_update) >= timedelta(hours=24)
        ):
            user.summary_count = get_daily_limit_for_role(user.role_id)
            user.counter_last_update = datetime.now()

        if user.summary_count <= 0:
            raise HTTPException(
                status_code=429,
                detail="You have reached your daily summary limit. Please, buy subscription :)",
            )

        user.summary_count -= 1
        self.session.add(user)
        self.session.commit()

        # Extract text from PDF
        with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
            text = chr(12).join([page.get_text() for page in doc])

        # Generate summary
        gemini_client = get_gemini_client()
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Summarize the following article {text} "
                     f"in the following style: {style} and length: {length}",
        )
        summary = response.text

        # Upload to GCS
        filename_hash = generate_hash(file.filename)
        destination_blob_name = f"summaries/{filename_hash}.txt"
        gcs_path = self.upload_text_to_gcs(summary, destination_blob_name)

        db_summary = Summary(filename=file.filename, filename_hash=filename_hash, user_id=user.id)
        self.session.add(db_summary)
        self.session.commit()
        self.session.refresh(db_summary)

        return summary, gcs_path

    def get_by_id(self, id: int):
        return self.session.exec(select(Summary).where(Summary.id == id)).first()

    def get_all_user_summaries(self, user_id: int):
        return self.session.exec(select(Summary).where(Summary.user_id == user_id)).all()


SummaryServiceDep = Annotated[SummaryService, Depends(SummaryService)]
