import fitz
from fastapi import UploadFile
from google import genai
from google.cloud import storage

from api.summary.dto.length import Length
from api.summary.dto.style import Style
from config import ai_settings

gemini_client = genai.Client(api_key=ai_settings.GEMINI_KEY)

storage_client = storage.Client()
bucket_name = "cbts-bucket"
bucket = storage_client.bucket(bucket_name)


def upload_text_to_gcs(text: str, destination_blob_name: str):
    print(list(storage_client.list_buckets()))

    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(text, content_type='text/plain')
    return blob.public_url


async def summarize_pdf(style: Style, length: Length, file: UploadFile):
    with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
        text = chr(12).join([page.get_text() for page in doc])

    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash", contents=f"Summarize the following article {text} in the following style: {style} and length: {length}"
    )
    summary = response.text

    destination_blob_name = f"summaries/{file.filename}.txt"
    gcs_path = upload_text_to_gcs(summary, destination_blob_name)

    return summary, gcs_path
