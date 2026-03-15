package com.citicup.controller;

import com.citicup.dto.news.NewsIngestRequest;
import com.citicup.service.NewsService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.Instant;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(NewsController.class)
class NewsControllerTest {

    @Autowired MockMvc mvc;
    @Autowired ObjectMapper objectMapper;
    @MockBean NewsService newsService;

    @Test
    void ingest_validRequest_returnsId() throws Exception {
        NewsIngestRequest req = NewsIngestRequest.builder()
                .source("Reuters").title("Oil rises sharply")
                .content("Market news content").url("http://reuters.com/article")
                .publishedAt(Instant.parse("2025-01-01T12:00:00Z"))
                .build();

        when(newsService.ingestAndScore(any())).thenReturn(1L);

        mvc.perform(post("/api/news/ingest")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data").value(1));
    }

    @Test
    void ingest_missingSource_returnsValidationError() throws Exception {
        NewsIngestRequest req = NewsIngestRequest.builder()
                .source("")              // @NotBlank violation
                .title("Oil rises")
                .publishedAt(Instant.now())
                .build();

        mvc.perform(post("/api/news/ingest")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(-1));
    }

    @Test
    void ingest_missingPublishedAt_returnsValidationError() throws Exception {
        NewsIngestRequest req = NewsIngestRequest.builder()
                .source("Reuters").title("Oil rises")
                .publishedAt(null)       // @NotNull violation
                .build();

        mvc.perform(post("/api/news/ingest")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(-1));
    }
}
