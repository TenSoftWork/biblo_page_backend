import uuid
import time
from fastapi import WebSocket, WebSocketDisconnect
from typing import AsyncGenerator
import json

from services.session import chat_sessions, ChatSession
from services.bert import classify_type
from services.llm import generate_streaming_response
from utils.helpers import format_timestamp


async def stream_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # 초기 연결 메시지 받기
        data = await websocket.receive_json()
        user_prompt = data.get("prompt")
        session_id = data.get("session_id")
        
        # 사용자 정보 추출 (WebSocket에서는 제한적으로만 가능)
        user_ip = websocket.client.host if hasattr(websocket, 'client') and websocket.client else "unknown"
        user_os = "unknown"
        user_browser = "unknown"
        
        if not user_prompt:
            await websocket.send_json({"error": "No prompt provided"})
            return
        
        # BERT 분류기를 이용해 타입 결정
        query_type = classify_type(user_prompt)
        
        # 세션 관리
        is_new_session = False
        if not session_id or session_id not in chat_sessions:
            new_session_id = str(uuid.uuid4())
            chat_sessions[new_session_id] = ChatSession(
                new_session_id, 
                query_type, 
                user_ip=user_ip, 
                user_os=user_os, 
                user_browser=user_browser
            )
            session = chat_sessions[new_session_id]
            session_id = new_session_id
            is_new_session = True
            
            # 세션 정보 전송
            await websocket.send_json({
                "type": "session_info",
                "session_id": new_session_id,
                "is_new_session": True
            })
        else:
            session = chat_sessions[session_id]
            session.query_type = query_type
            
            # 기존 세션 정보 전송 (세션 유지를 확인하기 위해)
            await websocket.send_json({
                "type": "session_info",
                "session_id": session_id,
                "is_new_session": False,
                "message_count": len(session.conversation_history)
            })
        
        # 사용자 메시지 저장
        user_message_id = session.add_message("user", user_prompt)
        
        # 중요: 여기서 생성된 assistant_message_id를 사용해 저장까지 일관되게 처리
        assistant_message_id = str(uuid.uuid4())
        await websocket.send_json({
            "type": "message_start",
            "message_id": assistant_message_id,
            "user_message_id": user_message_id,
            "session_id": session_id
        })
        
        # 스트리밍 응답 생성 및 전송
        full_response = ""
        async for chunk in generate_streaming_response(user_prompt, session, query_type):
            full_response += chunk
            await websocket.send_json({
                "type": "token",
                "token": chunk,
                "session_id": session_id
            })
        
        # 중요: 응답 완료 시 동일한 assistant_message_id로 메시지 저장
        session.add_message("🖥️ Biblo AI", full_response, assistant_message_id)
        
        # 응답 완료 메시지
        await websocket.send_json({
            "type": "message_end",
            "message_id": assistant_message_id,
            "full_response": full_response,
            "session_id": session_id,
            "conversation_history": [
                {
                    "id": msg["id"],
                    "role": msg["role"],
                    "content": msg["content"]
                } for msg in session.conversation_history
            ]
        })
        
    except WebSocketDisconnect:
        print("클라이언트 연결 해제")
    except Exception as e:
        print(f"WebSocket 오류: {str(e)}")
        await websocket.send_json({"error": str(e)})

# 세션 정리 함수
def cleanup_session(session_id: str):
    if session_id in chat_sessions:
        session = chat_sessions[session_id]
        print(f"세션 종료 및 정리: {session_id}")
        
        # 피드백 요약 정보 출력
        feedback_summary = session.get_feedback_summary()
        print(f"피드백 요약: {feedback_summary}")
        
        # 새로운 형식의 로그 출력 (포맷팅된 타임스탬프 사용)
        session_log = {
            "sessionID": session.session_id,
            "user_ip": session.user_ip,
            "user_os": session.user_os,
            "user_browser": session.user_browser,
            "session_start": session.created_at_formatted,  # 포맷팅된 타임스탬프 사용
            "session_end": session.last_interaction_formatted,  # 포맷팅된 타임스탬프 사용
            "chat": session.get_chat_log()
        }
        
        # 로그 출력
        print("세션 로그:")
        print(json.dumps(session_log, indent=2, ensure_ascii=False))
        
        # 메모리에서 세션 제거
        del chat_sessions[session_id]

async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            # 클라이언트가 연결되어 있는지 확인하기 위한 핑
            await websocket.receive_text()
            # 세션이 유효한지 확인
            if session_id in chat_sessions:
                chat_sessions[session_id].last_interaction = time.time()
    except WebSocketDisconnect:
        # 클라이언트 연결 해제 시 세션 정리하지 않고 로그만 기록
        if session_id in chat_sessions:
            print(f"WebSocket 연결 해제: 세션 {session_id} 활성 상태 유지")
        else:
            print(f"WebSocket 연결 해제: 세션 {session_id} 존재하지 않음")
    except Exception as e:
        print(f"WebSocket endpoint 오류: {str(e)}") 