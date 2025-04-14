import time
import uuid
import json
from typing import Dict, List
from langchain.memory import ConversationBufferMemory

from utils.helpers import format_timestamp

class ChatSession:
    def __init__(self, session_id: str, query_type: int, user_ip: str = None, user_os: str = None, user_browser: str = None):
        self.session_id = session_id
        self.query_type = query_type  # 0: 회사, 1: 도서관
        self.created_at = time.time()
        self.created_at_formatted = format_timestamp(self.created_at)
        self.last_interaction = time.time()
        self.last_interaction_formatted = format_timestamp(self.last_interaction)
        self.conversation_history = []
        self.memory = ConversationBufferMemory(return_messages=True)
        self.feedback = {}  # 메시지 ID와 피드백 저장용 딕셔너리
        
        # 사용자 정보 추가
        self.user_ip = user_ip
        self.user_os = user_os
        self.user_browser = user_browser
    
    def add_message(self, role: str, content: str, message_id: str = None):
        if message_id is None:
            message_id = str(uuid.uuid4())  # 고유한 메시지 ID 생성
        
        timestamp = time.time()
        message = {
            "id": message_id,
            "role": role,
            "content": content, 
            "timestamp": timestamp,
            "timestamp_formatted": format_timestamp(timestamp)
        }
        self.conversation_history.append(message)
        
        if role == "user":
            self.memory.save_context({"input": content}, {"output": ""})
        elif role == "🖥️ Biblo AI":
            # 이전 컨텍스트의 출력을 업데이트
            if self.conversation_history and len(self.conversation_history) >= 2:
                prev_context = self.memory.load_memory_variables({})
                prev_inputs = prev_context.get("history", [])
                if prev_inputs and len(prev_inputs) >= 1:
                    # 마지막 입력의 출력을 현재 어시스턴트 응답으로 설정
                    self.memory.save_context({"input": self.conversation_history[-2]["content"]}, {"output": content})
        
        self.last_interaction = time.time()
        self.last_interaction_formatted = format_timestamp(self.last_interaction)
        return message_id
    
    def add_feedback(self, message_id: str, feedback_value: int):
        """메시지 ID에 대한 피드백 추가 (1: 좋아요, 0: 싫어요)"""
        if message_id in [msg["id"] for msg in self.conversation_history]:
            self.feedback[message_id] = feedback_value
            return True
        return False
    
    def get_formatted_history(self) -> str:
        """대화 기록을 LLM 프롬프트용으로 포맷팅"""
        if not self.conversation_history:
            return "이전 대화 내용이 없습니다."
        
        history_text = "이전 대화 내용:\n"
        for msg in self.conversation_history:
            role_text = "👤 사용자" if msg["role"] == "user" else "🖥️ Biblo AI"
            history_text += f"{role_text}: {msg['content']}\n"
        return history_text
    
    def get_feedback_summary(self) -> dict:
        """피드백 통계 요약"""
        total_feedback = len(self.feedback)
        positive_feedback = sum(1 for v in self.feedback.values() if v == 1)
        
        return {
            "total_responses": sum(1 for msg in self.conversation_history if msg["role"] == "🖥️ Biblo AI"),
            "total_feedback": total_feedback,
            "positive_feedback": positive_feedback,
            "negative_feedback": total_feedback - positive_feedback,
            "feedback_ratio": positive_feedback / total_feedback if total_feedback > 0 else 0
        }
    
    def get_chat_log(self) -> list:
        """모든 채팅 로그 반환 (포맷팅된 타임스탬프 포함)"""
        chat_logs = []
        
        for i in range(0, len(self.conversation_history), 2):
            if i + 1 < len(self.conversation_history):
                user_msg = self.conversation_history[i]
                ai_msg = self.conversation_history[i + 1]
                
                # 해당 메시지에 대한 피드백 찾기
                feedback = self.feedback.get(ai_msg["id"], None)
                
                chat_logs.append({
                    "chatID": ai_msg["id"],
                    "chat_time": ai_msg["timestamp_formatted"],  # 포맷팅된 타임스탬프 사용
                    "user_prompt": user_msg["content"],
                    "assistant_prompt": ai_msg["content"],
                    "user_feedback": feedback
                })
        
        return chat_logs

# 채팅 세션 저장소
chat_sessions: Dict[str, ChatSession] = {} 