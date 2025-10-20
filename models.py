from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LogCreate(BaseModel):
    service: str
    level: str
    message: str
    details: Optional[dict] = None

class LogResponse(LogCreate):
    id: str
    timestamp: datetime
