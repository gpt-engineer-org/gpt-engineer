from pydantic import BaseModel
from typing import Dict

class LetterRequest(BaseModel):
    letter_template: str
    parameters: Dict[str, str]

class LetterResponse(BaseModel):
    message: str
    email_status: str