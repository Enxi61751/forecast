package com.citicup.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.Instant;

@Entity
@Table(name = "news_article")
@Data @NoArgsConstructor @AllArgsConstructor @Builder
public class NewsArticle {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable=false)
    private String source;   // Reuters/WSJ/...
    @Column(nullable=false, length=512)
    private String title;

    @Column(columnDefinition="TEXT")
    private String content;

    private String url;

    @Column(nullable=false)
    private Instant publishedAt;

    @Column(nullable=false)
    private Instant ingestedAt;
}