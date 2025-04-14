FROM python:3.13-slim

WORKDIR /app

# 필요한 시스템 패키지 설치 (빌드 도구)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 환경변수 설정
# API 키는 Docker 실행 시 --env-file .env 옵션으로 전달하거나 -e 옵션으로 직접 전달해야 합니다.
ENV PYTHONUNBUFFERED=1

# 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]