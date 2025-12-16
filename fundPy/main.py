# main.py
import json
import time
from kafka import KafkaConsumer, KafkaProducer
from config import Config
from rag_service import StockRAGService

def start_worker():
    # 1. AI 서비스 초기화
    rag_service = StockRAGService()

    # 2. Kafka Producer 설정
    producer = KafkaProducer(
        bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    # 3. Kafka Consumer 설정
    consumer = KafkaConsumer(
        Config.TOPIC_REQUEST,
        bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
        group_id='stock-ai-worker-group',
        auto_offset_reset='latest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    print(f"✅ Python Worker Started! Listening on '{Config.TOPIC_REQUEST}'...")

    # 4. 무한 루프 (메시지 대기)
    try:
        for message in consumer:
            data = message.value
            request_id = data.get('request_id')
            user_id = data.get('user_id') # 또는 session_id
            query = data.get('query')

            print(f"\n[Request Received] ID: {request_id} | Query: {query}")

            # AI 분석 수행
            start_time = time.time()
            answer = rag_service.generate_answer(query)
            end_time = time.time()

            # 결과 데이터 구성
            response_data = {
                'request_id': request_id,
                'user_id': user_id,
                'answer': answer,
                'processing_time': round(end_time - start_time, 2)
            }

            # Kafka로 결과 전송
            producer.send(Config.TOPIC_RESPONSE, value=response_data)
            producer.flush()
            print(f"[Response Sent] To: '{Config.TOPIC_RESPONSE}'")

    except KeyboardInterrupt:
        print("Worker stopped by user.")
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        consumer.close()
        producer.close()

if __name__ == "__main__":
    start_worker()