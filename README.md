# Biblo Page Backend

이 프로젝트는 도서관 및 회사 정보를 제공하는 AI 기반 백엔드 서비스입니다. FastAPI, LangChain, Milvus DB를 활용하여 사용자 질문에 대한 응답을 생성합니다.

## 프로젝트 구조

```
biblo_page_backend/
├── api/ - API 엔드포인트 및 웹소켓 관련 로직
│   ├── __init__.py
│   ├── routes.py - HTTP 엔드포인트 정의
│   ├── schemas.py - Pydantic 모델 정의
│   └── websocket.py - 웹소켓 핸들러
├── database/ - 데이터베이스 관련 로직
│   └── __init__.py
├── LLM/ - 언어 모델 관련 리소스
├── milvus/ - Milvus 벡터 데이터베이스 파일
├── services/ - 비즈니스 로직 관련 서비스
│   ├── __init__.py
│   ├── bert.py - BERT 분류기
│   ├── embeddings.py - 임베딩 관련 기능
│   ├── llm.py - LLM 관련 기능
│   └── session.py - 세션 관리
├── utils/ - 유틸리티 함수
│   ├── __init__.py
│   └── helpers.py
├── main.py - 앱 진입점
├── requirements.txt - 의존성 목록
├── Dockerfile - Docker 설정
├── .env - 환경변수 설정 파일 (보안 정보 포함)
└── README.md - 프로젝트 설명
```

## 설치 및 실행

### 환경변수 설정

프로젝트는 `.env` 파일을 통해 환경변수를 관리합니다. 아래와 같이 필요한 환경변수를 설정하세요:

1. 프로젝트 루트에 `.env` 파일 생성
2. 아래 내용 추가
```
# OpenAI API 키
OPENAI_API_KEY="your_openai_api_key_here"
```

### 로컬 환경에서 실행하기

1. 필요한 패키지 설치
```
pip install -r requirements.txt
```

2. 서버 실행
```
uvicorn main:app --reload
```

### Docker로 실행하기

1. Docker 이미지 빌드
```
docker build -t biblo-backend .
```

2. Docker 컨테이너 실행 (환경변수 파일 사용)
```
docker run -p 8000:8000 --env-file .env biblo-backend
```

또는 환경변수 직접 전달
```
docker run -p 8000:8000 -e OPENAI_API_KEY="your_openai_api_key_here" biblo-backend
```

## API 엔드포인트

- `/stream` (WebSocket): 스트리밍 응답 생성
- `/ws/{session_id}` (WebSocket): 세션 유지 및 관리
- `/extract_user_info` (POST): 사용자 정보 추출
- `/end_session` (POST): 세션 종료
- `/feedback` (POST): 사용자 피드백 제출 