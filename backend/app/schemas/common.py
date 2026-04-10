from pydantic import BaseModel
from typing import Optional, Any


class QuickReply(BaseModel):
    label: str
    value: str
    primary: Optional[bool] = False
    next: Optional[str] = None


class BaseResponse(BaseModel):
    session_id: Optional[int] = None
    conversation_state: Optional[str] = None
    session_status: Optional[str] = None
    message: Optional[str] = None
    quick_replies: Optional[list[QuickReply]] = None
    extra: Optional[dict[str, Any]] = None
