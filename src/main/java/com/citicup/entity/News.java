package com.citicup.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "news")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class News {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    private String source;

    @Column(columnDefinition = "TEXT")
    private String summary;

    private String url;

    private LocalDateTime publishedAt;

    private String sentimentLabel;

    private Double sentimentScore;
}