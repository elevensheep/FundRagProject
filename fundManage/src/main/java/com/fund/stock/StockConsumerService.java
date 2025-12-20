package com.fund.stock;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fund.stock.dao.StockDocument;
import com.fund.stock.dao.StockRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class StockConsumerService {

    private final StockRepository stockRepository;
    private final ObjectMapper objectMapper;

    @KafkaListener(topics = "stock-response", groupId = "stock-response-group")
    public void consume(String message) {
        try {
            log.info("Kafka 응답 수신: {}", message);

            // JSON 파싱
            Map<String, Object> responseData = objectMapper.readValue(message, Map.class);
            String requestId = (String) responseData.get("request_id");
            String answer = (String) responseData.get("answer");
            Double processingTime = ((Number) responseData.get("processing_time")).doubleValue();

            // MongoDB에서 문서 조회
            StockDocument document = stockRepository.findById(requestId)
                    .orElseThrow(() -> new RuntimeException("Document not found: " + requestId));

            // 응답 업데이트
            document.setAnswer(answer);
            document.setStatus("COMPLETED");
            document.setProcessingTime(processingTime);
            document.setCompletedAt(LocalDateTime.now());

            stockRepository.save(document);
            log.info("응답 저장 완료 - documentId: {}", requestId);

        } catch (Exception e) {
            log.error("Kafka 응답 처리 실패: {}", e.getMessage(), e);
        }
    }
}
