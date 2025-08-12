from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal, Any, List
from datetime import datetime

class TextModerationRequest(BaseModel):
    email: EmailStr
    text: str = Field(..., min_length=1, max_length=5000)

class ImageModerationRequest(BaseModel):
    email: EmailStr
    image_base64: str

class ModerationResultResponse(BaseModel):
    classification: Literal["toxic", "spam", "harassment", "safe"]
    confidence: float
    reasoning: Optional[str]
    llm_response: Optional[Any]

    model_config = dict(from_attributes=True)

class ModerationRequestResponse(BaseModel):
    id: int
    content_type: Literal["image", "text"]
    status: str
    created_at: datetime
    results: List[ModerationResultResponse] = Field(default_factory=list)

    model_config = dict(from_attributes=True)


class NotificationLogResponse(BaseModel):
    request_id: int
    channel: Literal["email", "slack"] 
    status: Literal["pending", "send"]  
    sent_at: datetime

    model_config = dict(from_attributes=True)

class AnalyticsSummaryResponse(BaseModel):
    user: EmailStr
    total_requests: int
    counts_by_classification: dict
    last_request_at: Optional[datetime]
    notification_logs: Optional[List[NotificationLogResponse]] = None

    model_config = dict(from_attributes=True)

class ModerationResult(BaseModel):
    content_type: Literal["text", "image"]
    classification: Literal["toxic", "spam", "harassment", "safe"]
    confidence: float
    reason: str
    description: str

