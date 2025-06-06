from pydantic import BaseModel
from typing import Optional

class OutreachResponse(BaseModel):
    category: str
    resume_file: str
    email_subject: str
    email_body: str
    notes: Optional[str] = None
