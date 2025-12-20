package com.fund.stock.dao;

import lombok.Builder;
import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import java.time.LocalDateTime;

@Data
@Builder
@Document(collection = "stock_questions") // MongoDB 컬렉션 이름
public class StockDocument {
    @Id
    private String id;
    private String userId;
    private String query;
    private String answer;
    private String status; // 예: "PENDING", "COMPLETED", "FAILED"
    private Double processingTime;
    private LocalDateTime createdAt;
    private LocalDateTime completedAt;
}