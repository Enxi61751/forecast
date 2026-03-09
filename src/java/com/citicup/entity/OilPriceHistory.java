package com.citicup.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "oil_price_history")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class OilPriceHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String type;

    @Column(nullable = false)
    private Double price;

    @Column(nullable = false)
    private String currency;

    @Column(nullable = false)
    private String unit;

    @Column(name = "change_percent")
    private String changePercent;

    @Column(nullable = false)
    private LocalDateTime timestamp;

}
