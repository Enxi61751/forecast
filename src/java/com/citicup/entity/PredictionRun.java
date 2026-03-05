package com.citicup.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.Instant;

@Entity
@Table(name="prediction_run")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class PredictionRun {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable=false)
    private String target;          // WTI / Brent
    @Column(nullable=false)
    private String horizon;         // 1d/7d/30d
    @Column(nullable=false)
    private Instant runAt;

    // 预测主结果（比如未来N天价格/区间，直接存 JSON 字符串方便）
    @Column(columnDefinition="TEXT")
    private String forecastJson;

    // 极端分类结果（TFT输出）
    @Column(columnDefinition="TEXT")
    private String extremeClsJson;
}