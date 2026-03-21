package com.citicup.controller;

import com.citicup.common.ApiResponse;
import com.citicup.dto.news.NewsIngestRequest;
import com.citicup.entity.News;
import com.citicup.service.NewsService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/news")
public class NewsController {

    private final NewsService newsService;

    public NewsController(NewsService newsService) {
        this.newsService = newsService;
    }

    @GetMapping("/list")
    public ApiResponse<Map<String, Object>> list() {
        List<News> newsList = newsService.getNewsList();
        return ApiResponse.ok(Map.of("total", newsList.size(), "list", newsList));
    }

    @PostMapping("/ingest")
    public ApiResponse<Long> ingest(@Valid @RequestBody NewsIngestRequest req) {
        Long id = newsService.ingestAndScore(req);
        return ApiResponse.ok(id);
    }
}
