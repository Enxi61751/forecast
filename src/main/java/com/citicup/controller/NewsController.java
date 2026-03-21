package com.citicup.controller;

import com.citicup.entity.News;
import com.citicup.service.NewsService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class NewsController {

    private final NewsService newsService;

    public NewsController(NewsService newsService) {
        this.newsService = newsService;
    }

    @GetMapping("/api/news/list")
    public Map<String, Object> list() {
        List<News> newsList = newsService.getNewsList();

        Map<String, Object> result = new HashMap<>();
        result.put("code", 0);
        result.put("message", "success");

        Map<String, Object> data = new HashMap<>();
        data.put("total", newsList.size());
        data.put("list", newsList);

        result.put("data", data);
        return result;
    }
}