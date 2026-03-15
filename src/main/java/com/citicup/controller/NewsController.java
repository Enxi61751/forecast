package com.citicup.controller;

import com.citicup.common.ApiResponse;
import com.citicup.dto.news.NewsIngestRequest;
import com.citicup.service.NewsService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/news")
@RequiredArgsConstructor
public class NewsController {

    private final NewsService newsService;

    @PostMapping("/ingest")
    public ApiResponse<Long> ingest(@Valid @RequestBody NewsIngestRequest req) {
        Long id = newsService.ingestAndScore(req);
        return ApiResponse.ok(id);
    }
}