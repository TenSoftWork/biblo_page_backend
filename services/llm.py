from typing import AsyncGenerator
from langchain_openai import ChatOpenAI
from services.embeddings import search_company_collections, search_biblo_collections
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# OpenAI LLM 초기화
llm = ChatOpenAI(
    model="gpt-4-turbo",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    max_retries=1024,
    streaming=True  # 스트리밍 모드 활성화
)

# 프롬프트 템플릿
LIBRARY_PROMPT = """
As a librarian, you are expected to provide users with accurate and reliable information about the university library. 
Your role is to answer the user's queries: {user_query} based on the provided information: {context} and their previous conversation history: {user_history}.

[Response Guidelines]
- Ensure that responses are factually accurate and strictly adhere to the provided context without adding extra information.
- Prioritize key details exactly as described in the source document.
- Structure responses in a clear and professional manner, using 7 sentences.
- If the question is ambiguous, ask for clarification before providing an answer.
- If the query is outside the provided context, state that you can only provide information related to the university library.

[Strong System Rules]
- The response must follow the exact format below without additional text or explanations:
  
1) Biblo Univ Librarian:
- Provide a direct and precise answer to the question in 7 sentences in Korean, strictly following the given context.

[Example Response Format]
비블로대학교 도서관 이용 규칙은 다음과 같습니다. 도서관 운영 시간은 평일 08:00~22:00, 주말 및 공휴일 09:00~18:00이며, 시험 기간에는 24시간 개방됩니다. 자료 대출은 학부생 5권(14일), 대학원생 10권(30일), 교수 및 연구진 15권(60일)까지 가능합니다. 도서관 내에서는 음식물 반입이 금지되며, 휴대전화는 무음 모드로 설정해야 합니다. 그룹 스터디룸은 최소 3인 이상이 예약할 수 있으며, 최대 2시간 동안 사용할 수 있습니다. 연체료는 1일당 500원이며, 분실 시 동일 도서를 구매하여 반납하거나 변상금을 납부해야 합니다. 보다 자세한 정보는 도서관 홈페이지에서 확인할 수 있습니다.

"""

SERVICE_PROMPT = """
As a company representative of Ten Softworks, your role is to provide users with precise and reliable information about the company, its AI Agent technology, and its services. Your response must be based strictly on the provided company information: {context}, the user's query: {user_query}, and their previous conversation history: {user_history}.

[Response Guidelines]
- Ensure factual accuracy by strictly adhering to the provided {context}.
- Provide a concise yet informative response in 7 sentences.
- Maintain a professional and engaging tone.
- If the query is unclear, ask for clarification.
- If the question is outside Ten Softworks's scope, politely state that you can only provide information related to Ten Softworks.

[Strong System Rules]
- The response must follow the exact format below without any additional text or explanations:
- Provide a direct and precise answer to the question in 7 sentences in Korean, strictly following the given context.

[Example Response Format]
Ten Softworks는 AI 검색엔진 기술을 선도하는 글로벌 IT 기업입니다. 2022년에 설립되었으며, AI 기반 검색 솔루션 개발을 통해 정보 접근성을 극대화하는 것을 목표로 합니다. 주요 사업으로는 AI 검색엔진 개발, 자연어 처리(NLP) 최적화, 맞춤형 검색 솔루션 구축 및 실시간 데이터 분석이 포함됩니다. Ten Softworks의 대표 제품인 Biblo AI는 딥러닝 및 자연어 처리 기술을 활용하여 빠르고 정확한 검색 경험을 제공합니다. Biblo AI는 강화학습(RLHF)과 벡터 검색 기술을 활용하여 검색 정확도를 지속적으로 개선합니다. 주요 파트너로는 Google, OpenAI, KAIST 등이 있으며, 금융, 전자상거래, 헬스케어 분야에 검색 솔루션을 제공하고 있습니다. 보다 자세한 정보는 공식 홈페이지(https://soft.tsw.im/)에서 확인할 수 있습니다.

"""

async def generate_streaming_response(
    prompt: str, 
    session, 
    query_type: int
) -> AsyncGenerator[str, None]:
    try:
        # 검색 결과와 프롬프트 선택
        if query_type == 0:
            # 회사 관련 (텐소프트웍스)
            context = search_company_collections(prompt)
            selected_prompt = SERVICE_PROMPT
        else:
            # 비블로 관련 (도서관)
            context = search_biblo_collections(prompt)
            selected_prompt = LIBRARY_PROMPT
        
        # 이전 대화 내용 가져오기
        user_history = session.get_formatted_history()
        
        # 프롬프트 생성
        formatted_prompt = selected_prompt.format(
            user_query=prompt, 
            context=context,
            user_history=user_history
        )
        print(f"📃 Prompt: {formatted_prompt}")
        
        # 스트리밍 응답 생성
        full_response = ""
        async for chunk in llm.astream(formatted_prompt):
            if isinstance(chunk, str):
                chunk_text = chunk
            else:
                # AI 응답 객체에서 텍스트 추출
                chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
            
            full_response += chunk_text
            yield chunk_text
        
    except Exception as e:
        error_message = f"스트리밍 응답 생성 중 오류: {str(e)}"
        print(error_message)
        yield error_message 