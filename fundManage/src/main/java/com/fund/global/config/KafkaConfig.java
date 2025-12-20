package com.fund.global.config;

import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;

@Configuration
public class KafkaConfig {

    // "stock-request"라는 이름의 토픽을 자동 생성
    @Bean
    public NewTopic stockRequestTopic() {
        return TopicBuilder.name("stock-request")
                .partitions(1)
                .replicas(1)
                .build();
    }
}