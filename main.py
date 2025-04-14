import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

from api import api_router
from api.websocket import stream_endpoint, websocket_endpoint

# FastAPI 애플리케이션 생성
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://biblo.ai", "http://biblo.ai", "wss://biblo.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router)

# WebSocket 엔드포인트 등록
app.websocket("/stream")(stream_endpoint)
app.websocket("/ws/{session_id}")(websocket_endpoint)

# 서버 시작 이벤트
@app.on_event("startup")
async def startup_event():
    # 서버 시작 시 이벤트 핸들러
    print("서버 시작: 세션 관리 시스템 초기화")
    print("CORS 설정된 허용 오리진:", app.middleware_stack.__dict__.get("middlewares", [])[0].__dict__.get("options", {}).get("allow_origins", []))

# 서버 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    from api.websocket import cleanup_session
    from services.session import chat_sessions
    # 서버 종료 시 이벤트 핸들러
    # 모든 세션 정리 및 RDBMS 저장
    sessions_to_cleanup = list(chat_sessions.keys())
    for session_id in sessions_to_cleanup:
        cleanup_session(session_id)

# 앱 실행 (개발용)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)