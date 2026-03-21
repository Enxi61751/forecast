package com.citicup.service;

import com.citicup.dto.news.NewsIngestRequest;
import com.citicup.dto.news.SentimentResponse;
import com.citicup.entity.ExtremeEvent;
import com.citicup.entity.News;
import com.citicup.entity.NewsArticle;
import com.citicup.entity.SentimentScore;
import com.citicup.repository.ExtremeEventRepo;
import com.citicup.repository.NewsArticleRepo;
import com.citicup.repository.NewsRepository;
import com.citicup.repository.SentimentScoreRepo;
import com.citicup.service.client.ModelServiceClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.logging.Logger;

@Service
public class NewsService {

    private static final Logger logger = Logger.getLogger(NewsService.class.getName());

    @Autowired
    private NewsArticleRepo newsArticleRepo;

    @Autowired
    private SentimentScoreRepo sentimentScoreRepo;

    @Autowired
    private ExtremeEventRepo extremeEventRepo;

    @Autowired
    private ModelServiceClient modelServiceClient;

    @Autowired
    private NewsRepository newsRepository;

    public List<News> getNewsList() {
        return newsRepository.findAll();
    }

    public Long ingestAndScore(NewsIngestRequest req) {
        // Step 1: save the article first (independent transaction)
        Long newsId = saveArticle(req);

        // Step 2: call model service outside the DB transaction
        // If this fails, the article is still saved
        try {
            SentimentResponse sr = modelServiceClient.scoreNews(req);
            saveSentiment(newsId, sr);
        } catch (Exception e) {
            logger.warning("Sentiment scoring failed for newsId=" + newsId + ": " + e.getMessage());
        }

        return newsId;
    }

    @Transactional
    protected Long saveArticle(NewsIngestRequest req) {
        NewsArticle saved = newsArticleRepo.save(
                NewsArticle.builder()
                        .source(req.getSource())
                        .title(req.getTitle())
                        .content(req.getContent())
                        .url(req.getUrl())
                        .publishedAt(req.getPublishedAt())
                        .ingestedAt(Instant.now())
                        .build()
        );
        return saved.getId();
    }

    @Transactional
    protected void saveSentiment(Long newsId, SentimentResponse sr) {
        sentimentScoreRepo.save(
                SentimentScore.builder()
                        .newsId(newsId)
                        .sentiment(sr.getSentiment())
                        .confidence(sr.getConfidence())
                        .scoredAt(Instant.now())
                        .build()
        );

        if (sr.getExtremeEvents() != null) {
            for (SentimentResponse.ExtremeEventDto e : sr.getExtremeEvents()) {
                extremeEventRepo.save(
                        ExtremeEvent.builder()
                                .newsId(newsId)
                                .eventType(e.getEventType())
                                .summary(e.getSummary())
                                .intensity(e.getIntensity())
                                .occurredAt(Instant.parse(e.getOccurredAt()))
                                .createdAt(Instant.now())
                                .build()
                );
            }
        }
    }
}
