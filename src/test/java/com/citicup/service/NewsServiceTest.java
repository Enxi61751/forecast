package com.citicup.service;

import com.citicup.dto.news.NewsIngestRequest;
import com.citicup.dto.news.SentimentResponse;
import com.citicup.entity.NewsArticle;
import com.citicup.entity.SentimentScore;
import com.citicup.repository.ExtremeEventRepo;
import com.citicup.repository.NewsArticleRepo;
import com.citicup.repository.SentimentScoreRepo;
import com.citicup.service.client.ModelServiceClient;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class NewsServiceTest {

    @Mock NewsArticleRepo newsRepo;
    @Mock SentimentScoreRepo scoreRepo;
    @Mock ExtremeEventRepo eventRepo;
    @Mock ModelServiceClient modelClient;
    @InjectMocks NewsService newsService;

    private NewsIngestRequest buildReq() {
        return NewsIngestRequest.builder()
                .source("Reuters").title("Oil price rises")
                .content("Oil market content").url("http://example.com")
                .publishedAt(Instant.now()).build();
    }

    @Test
    void ingestAndScore_noExtremeEvents_returnsSavedId() {
        NewsIngestRequest req = buildReq();
        NewsArticle saved = NewsArticle.builder()
                .id(7L).source("Reuters").title("Oil price rises")
                .ingestedAt(Instant.now()).publishedAt(Instant.now()).build();
        when(newsRepo.save(any())).thenReturn(saved);

        SentimentResponse sr = SentimentResponse.builder()
                .sentiment(0.6).confidence(0.85).extremeEvents(null).build();
        when(modelClient.scoreNews(req)).thenReturn(sr);
        when(scoreRepo.save(any())).thenReturn(new SentimentScore());

        Long id = newsService.ingestAndScore(req);

        assertEquals(7L, id);
        verify(scoreRepo).save(any());
        verify(eventRepo, never()).save(any());
    }

    @Test
    void ingestAndScore_withExtremeEvents_savesEvents() {
        NewsIngestRequest req = buildReq();
        NewsArticle saved = NewsArticle.builder()
                .id(8L).source("Reuters").title("Oil price rises")
                .ingestedAt(Instant.now()).publishedAt(Instant.now()).build();
        when(newsRepo.save(any())).thenReturn(saved);

        SentimentResponse.ExtremeEventDto evt = new SentimentResponse.ExtremeEventDto();
        evt.setEventType("PRICE_SPIKE");
        evt.setSummary("Significant price spike detected");
        evt.setIntensity(0.9);
        evt.setOccurredAt("2025-01-01T00:00:00Z");

        SentimentResponse sr = SentimentResponse.builder()
                .sentiment(0.8).confidence(0.95).extremeEvents(List.of(evt)).build();
        when(modelClient.scoreNews(req)).thenReturn(sr);
        when(scoreRepo.save(any())).thenReturn(new SentimentScore());

        Long id = newsService.ingestAndScore(req);

        assertEquals(8L, id);
        verify(eventRepo).save(any());
    }
}
