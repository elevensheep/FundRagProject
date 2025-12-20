# rag_service.py
from google import genai
from pinecone import Pinecone
from config import Config

class StockRAGService:
    def __init__(self):
        # 1. Gemini 설정
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)

        # 2. Pinecone 설정
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
        print(">> AI Service Initialized (Gemini + Pinecone)")

    def generate_answer(self, user_query):
        try:
            # 1. 쿼리 임베딩
            embedding_result = self.client.models.embed_content(
                model="models/text-embedding-004",
                contents=user_query
            )
            user_vector = embedding_result.embeddings[0].values

            # 2. Pinecone 검색
            search_results = self.index.query(
                vector=user_vector,
                top_k=3,
                include_metadata=True
            )

            # 3. 문맥(Context) 조립
            contexts = [match['metadata']['text'] for match in search_results['matches'] if 'text' in match['metadata']]
            context_str = "\n\n".join(contexts) if contexts else "관련된 뉴스를 찾을 수 없습니다."

            # 4. 프롬프트 작성
            prompt = f"""
            당신은 냉철한 주식 투자 전문가입니다.
            아래 [관련 뉴스]를 근거로 [사용자 질문]에 대해 논리적으로 답변하세요.
            마지막에는 반드시 "투자의 책임은 본인에게 있습니다."라는 문구를 포함하세요.

            [관련 뉴스]
            {context_str}

            [사용자 질문]
            {user_query}
            """

            # 5. 답변 생성
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            return response.text

        except Exception as e:
            print(f"Error generating answer: {e}")
            import traceback
            traceback.print_exc()
            return "죄송합니다. 분석 중 오류가 발생했습니다."
