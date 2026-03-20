package com.citicup.service;

import com.citicup.dto.news.NewsIngestRequest;
import com.citicup.dto.news.SentimentResponse;
import com.citicup.entity.ExtremeEvent;
import com.citicup.entity.NewsArticle;
import com.citicup.entity.SentimentScore;
import com.citicup.repository.ExtremeEventRepo;
import com.citicup.repository.NewsArticleRepo;
import com.citicup.repository.SentimentScoreRepo;
import com.citicup.service.client.ModelServiceClient;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
@RequiredArgsConstructor
public class NewsService {

    private final NewsArticleRepo newsRepo;
    private final SentimentScoreRepo scoreRepo;
    private final ExtremeEventRepo eventRepo;
    private final ModelServiceClient modelClient;

    @Transactional
    public Long ingestAndScore(NewsIngestRequest req) {
        NewsArticle saved = newsRepo.save(
                NewsArticle.builder()
                        .source(req.getSource())
                        .title(req.getTitle())
                        .content(req.getContent())
                        .url(req.getUrl())
                        .publishedAt(req.getPublishedAt())
                        .ingestedAt(Instant.now())
                        .build()
        );

        // 调 FastAPI 做情绪 + 极端事件识别
        SentimentResponse sr = modelClient.scoreNews(req);

        scoreRepo.save(
                SentimentScore.builder()
                        .newsId(saved.getId())
                        .sentiment(sr.getSentiment())
                        .confidence(sr.getConfidence())
                        .scoredAt(Instant.now())
                        .build()
        );

        if (sr.getExtremeEvents() != null) {
            for (var e : sr.getExtremeEvents()) {
                eventRepo.save(
                        ExtremeEvent.builder()
                                .newsId(saved.getId())
                                .eventType(e.getEventType())
                                .summary(e.getSummary())
                                .intensity(e.getIntensity())
                                .occurredAt(Instant.parse(e.getOccurredAt()))
                                .createdAt(Instant.now())
                                .build()
                );
            }
        }

        return saved.getId();
    }
}