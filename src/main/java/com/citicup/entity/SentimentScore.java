package com.citicup.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.Instant;

@Entity
@Table(name="sentiment_score", indexes = @Index(name="idx_news_id", columnList="newsId"))
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class SentimentScore {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable=false)
    private Long newsId;

    // [-1,1] 或 [0,1] 你们定义
    @Column(nullable=false)
    private Double sentiment;

    // 置信度
    private Double confidence;

    @Column(nullable=false)
    private Instant scoredAt;
}