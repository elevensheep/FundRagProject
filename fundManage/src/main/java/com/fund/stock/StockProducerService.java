package com.fund.stock;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fund.stock.dao.StockDocument;
import com.fund.stock.dao.StockRepository;
import com.fund.stock.StockRequestDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.concurrent.CompletableFuture;

@Slf4j
@Service
@RequiredArgsConstructor
public class StockProducerService {

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final StockRepository stockRepository; // DB 저장용
    private final ObjectMapper objectMapper;       // JSON 변환용

    @Transactional
    public String processAndSend(StockRequestDto requestDto) {
        // 1. MongoDB에 "질문 접수됨" 상태로 저장 (이력 관리)
        StockDocument document = StockDocument.builder()
                .userId(requestDto.getUserId())
                .query(requestDto.getQuery())
                .status("PENDING") // 대기 중
                .createdAt(LocalDateTime.now())
                .build();

        StockDocument savedDocument = stockRepository.save(document);
        log.info("DB 저장 완료 - ID: {}, userId: {}", savedDocument.getId(), savedDocument.getUserId());

        // 2. Kafka 메시지 생성 (Python이 기대하는 형식)
        String jsonMessage;
        try {
            var kafkaMessage = new java.util.HashMap<String, String>();
            kafkaMessage.put("request_id", savedDocument.getId());
            kafkaMessage.put("user_id", requestDto.getUserId());
            kafkaMessage.put("query", requestDto.getQuery());
            jsonMessage = objectMapper.writeValueAsString(kafkaMessage);
        } catch (JsonProcessingException e) {
            log.error("JSON 변환 실패: {}", requestDto, e);
            throw new RuntimeException("메시지 형식 변환 실패", e);
        }

        // 3. Kafka로 메시지 전송 (Python AI가 가져가도록)
        String topic = "stock-request";
        try {
            CompletableFuture<SendResult<String, String>> future = kafkaTemplate.send(topic, jsonMessage);

            // 전송 결과 확인
            future.whenComplete((result, ex) -> {
                if (ex != null) {
                    log.error("Kafka 전송 실패 - documentId: {}, error: {}", savedDocument.getId(), ex.getMessage());
                    // 실패 시 상태 업데이트
                    savedDocument.setStatus("FAILED");
                    savedDocument.setCompletedAt(LocalDateTime.now());
                    stockRepository.save(savedDocument);
                } else {
                    log.info("Kafka 전송 성공 - documentId: {}, partition: {}",
                            savedDocument.getId(), result.getRecordMetadata().partition());
                }
            });

            log.info("Kafka 전송 요청 완료 - documentId: {}", savedDocument.getId());
            return savedDocument.getId();

        } catch (Exception e) {
            log.error("Kafka 전송 중 예외 발생 - documentId: {}", savedDocument.getId(), e);
            // 상태를 FAILED로 업데이트
            savedDocument.setStatus("FAILED");
            savedDocument.setCompletedAt(LocalDateTime.now());
            stockRepository.save(savedDocument);
            throw new RuntimeException("메시지 전송 실패", e);
        }
    }
}