package com.citicup.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;

@Entity
@Table(name = "indicator_daily")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class IndicatorDaily {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private LocalDate date;

    @Column(name = "event_count", nullable = false)
    private Integer eventCount;

    @Column(name = "pos_count", nullable = false)
    private Integer posCount;

    @Column(name = "neg_count", nullable = false)
    private Integer negCount;

    @Column(name = "sentiment_sum")
    private Double sentimentSum;

    @Column(name = "sentiment_mean")
    private Double sentimentMean;

    @Column(name = "max_abs_sentiment")
    private Double maxAbsSentiment;
}
