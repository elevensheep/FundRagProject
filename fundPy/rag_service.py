# rag_service.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from config import Config

class StockRAGService:
    def __init__(self):
        # 0. 키 설정
        gemini_key = (Config.GEMINI_API_KEY or "").strip()
        pinecone_key = (Config.PINECONE_API_KEY or "").strip()

        if not gemini_key:
            raise ValueError("GEMINI_API_KEY가 설정되어 있지 않습니다.")
        if not pinecone_key:
            raise ValueError("PINECONE_API_KEY가 설정되어 있지 않습니다.")

        os.environ["GOOGLE_API_KEY"] = gemini_key
        os.environ["PINECONE_API_KEY"] = pinecone_key
        
        # 1. 임베딩 모델 설정
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

        # 2. Pinecone 벡터 스토어 설정
        self.vectorstore = PineconeVectorStore(
            index_name=Config.PINECONE_INDEX_NAME,
            embedding=self.embeddings
        )

        # 3. LLM 설정 (Gemini)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        # 4. RAG 체인 구성
        self._setup_rag_chain()
        print(">> AI Service Initialized (LangChain + Gemini + Pinecone)")

    def _setup_rag_chain(self):
        # 프롬프트 템플릿 정의
        template = """
        당신은 냉철한 주식 투자 전문가입니다.
        아래 [최근 관련 뉴스]를 근거로 [사용자 질문]에 대해 논리적으로 답변하세요.
        단계별로 생각해서 답변하세요.

        [최근 관련 뉴스]
        {context}

        [사용자 질문]
        {question}
        """
        prompt = ChatPromptTemplate.from_template(template)

        # 검색기(Retriever) 설정
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})

        # 컨텍스트 포맷팅 함수
        def format_docs(docs):
            if not docs:
                return "관련된 뉴스를 찾을 수 없습니다."
            return "\n\n".join(doc.page_content for doc in docs)

        # 체인 생성 (LCEL: LangChain Expression Language)
        self.rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def generate_answer(self, user_query):
        try:
            # RAG 체인 실행
            response = self.rag_chain.invoke(user_query)
            return response
        except Exception as e:
            print(f"Error generating answer: {e}")
            import traceback
            traceback.print_exc()
            return "죄송합니다. 분석 중 오류가 발생했습니다."
