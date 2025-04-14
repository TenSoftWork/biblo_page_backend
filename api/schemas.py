from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    stream: Optional[bool] = False  # 스트리밍 모드 요청 여부

class SessionEndRequest(BaseModel):
    session_id: str

class ExtractUserInfoRequest(BaseModel):
    session_id: str

class FeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    feedback_value: int  # 1: 좋아요, 0: 싫어요 