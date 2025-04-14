import torch
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus

# 임베딩 모델 초기화
device = "cuda:0" if torch.cuda.is_available() else "cpu"
embedding_model = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask",
    model_kwargs={"device": device}
)

# Milvus 컬렉션 연결
company_store = Milvus(
    embedding_function=embedding_model,
    collection_name="bibliography_collection",
    connection_args={"uri": "./database/milvus/milvus_demo.db"}
)
biblo_store = Milvus(
    embedding_function=embedding_model,
    collection_name="syllabus_collection",
    connection_args={"uri": "./database/milvus/milvus_demo.db"}
)

def search_company_collections(query, store=company_store, top_k=3):
    query_embedding = embedding_model.embed_query(query)
    company_results = store.similarity_search_by_vector(query_embedding, k=top_k)
    
    # 테스트용: 검색된 결과를 상세히 출력
    print("=== Company Collection 검색 결과 ===")
    for res in company_results:
        print(f"{res.page_content}\n")
    
    context = "\n".join(
        f"핵심정보: {res.page_content} \n{res.metadata.get('source_text', '')}" for res in company_results
    )
    return context

def search_biblo_collections(query, store=biblo_store, top_k=3):
    query_embedding = embedding_model.embed_query(query)
    biblo_results = store.similarity_search_by_vector(query_embedding, k=top_k)
    
    # 테스트용: 검색된 결과를 상세히 출력
    print("=== Biblo Collection 검색 결과 ===")
    for res in biblo_results:
        print(f"{res.page_content}\n")
    
    context = "\n".join(
        f"핵심정보: {res.page_content} \n{res.metadata.get('source_text', '')}" for res in biblo_results
    )
    return context 