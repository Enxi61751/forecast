package com.citicup.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.Instant;

@Entity
@Table(name="risk_report")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class RiskReport {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long predictionRunId;

    @Column(nullable=false)
    private Instant createdAt;

    @Column(columnDefinition="TEXT")
    private String reportText;      // 面向银行团队的文字报告

    @Column(columnDefinition="TEXT")
    private String materialsJson;   // 多智能体解释材料、证据链等
}