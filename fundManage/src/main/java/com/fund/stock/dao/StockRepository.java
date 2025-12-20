package com.fund.stock.dao;

import org.springframework.data.mongodb.repository.MongoRepository;

public interface StockRepository extends MongoRepository<StockDocument, String> {
    // 필요하면 여기에 findByUserId 같은 메서드 추가 가능
}