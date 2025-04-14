import datetime
from fastapi import Request
from user_agents import parse

def format_timestamp(timestamp):
    """Unix 타임스탬프를 읽기 좋은 형식으로 변환"""
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def extract_user_info(request: Request):
    """요청에서 사용자 IP, OS, 브라우저 정보 추출"""
    client_host = request.client.host if request.client else "unknown"
    
    user_agent_string = request.headers.get("user-agent", "")
    user_agent = parse(user_agent_string)
    
    os_info = f"{user_agent.os.family} {user_agent.os.version_string}"
    browser_info = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    
    return {
        "ip": client_host,
        "os": os_info,
        "browser": browser_info
    } 