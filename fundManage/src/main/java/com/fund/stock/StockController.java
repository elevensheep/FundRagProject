package com.fund.stock;

import com.fund.stock.dao.StockDocument;
import com.fund.stock.dao.StockRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/stock")
@RequiredArgsConstructor
public class StockController {

    private final StockProducerService stockProducerService;
    private final StockRepository stockRepository;

    @PostMapping("/ask")
    public ResponseEntity<Map<String, Object>> askStock(@Valid @RequestBody StockRequestDto requestDto) {
        Map<String, Object> response = new HashMap<>();

        try {
            // 서비스 계층 호출
            String documentId = stockProducerService.processAndSend(requestDto);

            response.put("success", true);
            response.put("message", "질문이 정상적으로 접수되었습니다.");
            response.put("documentId", documentId);

            log.info("질문 접수 성공 - userId: {}, documentId: {}", requestDto.getUserId(), documentId);
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("질문 접수 실패 - userId: {}, error: {}", requestDto.getUserId(), e.getMessage(), e);

            response.put("success", false);
            response.put("message", "질문 접수 중 오류가 발생했습니다: " + e.getMessage());

            return ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(response);
        }
    }

    @GetMapping("/result/{documentId}")
    public ResponseEntity<Map<String, Object>> getResult(@PathVariable String documentId) {
        Map<String, Object> response = new HashMap<>();

        try {
            StockDocument document = stockRepository.findById(documentId)
                    .orElseThrow(() -> new RuntimeException("문서를 찾을 수 없습니다."));

            response.put("success", true);
            response.put("status", document.getStatus());
            response.put("query", document.getQuery());

            if ("COMPLETED".equals(document.getStatus())) {
                response.put("answer", document.getAnswer());
                response.put("processingTime", document.getProcessingTime());
            }

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("결과 조회 실패 - documentId: {}, error: {}", documentId, e.getMessage(), e);

            response.put("success", false);
            response.put("message", "결과 조회 중 오류가 발생했습니다: " + e.getMessage());

            return ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(response);
        }
    }
}