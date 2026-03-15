package com.citicup.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "indicator_daily")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class IndicatorDaily {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
}
