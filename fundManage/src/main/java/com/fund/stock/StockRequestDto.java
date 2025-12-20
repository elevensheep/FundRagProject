package com.fund.stock;

import lombok.Data;
import jakarta.validation.constraints.NotBlank;

@Data
public class StockRequestDto {
    @NotBlank(message = "사용자 ID는 필수입니다")
    private String userId; // 질문자 ID

    @NotBlank(message = "질문 내용은 필수입니다")
    private String query;  // 질문 내용 (예: "삼성전자 전망 알려줘")
}