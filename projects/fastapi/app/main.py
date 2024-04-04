from fastapi import FastAPI, HTTPException
from . import models, schemas, email_service
from .config import settings
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/send-letter", response_model=schemas.LetterResponse)
async def send_letter(letter_request: schemas.LetterRequest):
    try:
        rendered_content = email_service.render_template(letter_request.letter_template, letter_request.parameters)
        await email_service.send_email("topsss1@yandex.ru", "test_letter", rendered_content)
        return schemas.LetterResponse(message="Email sent successfully", email_status="Sent")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))