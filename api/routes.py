from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from api.schemas import QueryRequest, SessionEndRequest, ExtractUserInfoRequest, FeedbackRequest
from api.websocket import cleanup_session
from services.session import chat_sessions
from utils.helpers import extract_user_info

router = APIRouter()

@router.post("/extract_user_info")
async def extract_user_info_endpoint(payload: ExtractUserInfoRequest, req: Request):
    # Request로부터 사용자 정보 추출
    user_info = extract_user_info(req)
    session_id = payload.session_id
    
    # 해당 session_id가 존재하는지 확인
    if session_id in chat_sessions:
        session = chat_sessions[session_id]
        # 세션의 사용자 정보 업데이트
        session.user_ip = user_info['ip']
        session.user_os = user_info['os']
        session.user_browser = user_info['browser']
    else:
        raise HTTPException(status_code=404, detail="Session not found")
    
@router.post("/end_session")
async def end_session(request: SessionEndRequest):
    """채팅 세션 종료 API"""
    session_id = request.session_id
    if session_id in chat_sessions:
        cleanup_session(session_id)
        return {"status": "success", "message": "Session ended successfully"}
    else:
        return {"status": "error", "message": "Session not found"}

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """세션 정보를 조회하는 API"""
    if session_id in chat_sessions:
        session = chat_sessions[session_id]
        return {
            "status": "success",
            "session_id": session_id,
            "message_count": len(session.conversation_history),
            "conversation_history": [
                {
                    "id": msg["id"],
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp_formatted": msg["timestamp_formatted"]
                } for msg in session.conversation_history
            ]
        }
    else:
        return {"status": "error", "message": "Session not found"}
    
@router.post("/feedback")
async def feedback_endpoint(request: FeedbackRequest):
    """사용자 피드백을 받는 API"""
    session_id = request.session_id
    message_id = request.message_id
    feedback_value = request.feedback_value
    
    # 피드백 값 유효성 검사
    if feedback_value not in [0, 1]:
        return {"status": "error", "message": "Invalid feedback value. Must be 0 (dislike) or 1 (like)."}
    
    # 세션 존재 여부 확인
    if session_id not in chat_sessions:
        return {"status": "error", "message": "Session not found."}
    
    # 피드백 추가
    session = chat_sessions[session_id]
    if session.add_feedback(message_id, feedback_value):
        return {
            "status": "success", 
            "message": "Feedback recorded successfully.",
            "feedback_summary": session.get_feedback_summary()
        }
    else:
        return {"status": "error", "message": "Message ID not found in this session."} 