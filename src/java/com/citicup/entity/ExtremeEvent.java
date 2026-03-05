package com.citicup.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.Instant;

@Entity
@Table(name="extreme_event")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class ExtremeEvent {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long newsId;           // 关联新闻（也可为空，表示指标触发）
    @Column(nullable=false)
    private String eventType;      // e.g. "GeoPoliticalShock", "SupplyCut", "OPEC"
    @Column(length=1024)
    private String summary;        // 事件摘要（LLM/规则生成）
    private Double intensity;      // 强度(0-1 或 0-100)

    @Column(nullable=false)
    private Instant occurredAt;

    private Instant createdAt;
}