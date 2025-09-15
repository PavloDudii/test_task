from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int
    details: Optional[dict] = None
