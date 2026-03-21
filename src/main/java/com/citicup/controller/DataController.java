package com.citicup.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class DataController {

    @GetMapping("/api/data/events")
    public Map<String, Object> events() {
        Map<String, Object> result = new HashMap<>();
        result.put("code", 0);
        result.put("message", "success");

        Map<String, Object> data = new HashMap<>();
        data.put("total", 2);
        data.put("list", List.of(
                Map.of("id", 1, "name", "Event A", "date", "2026-03-19"),
                Map.of("id", 2, "name", "Event B", "date", "2026-03-20")
        ));

        result.put("data", data);
        return result;
    }

    @GetMapping("/api/data/exchange")
    public Map<String, Object> exchange() {
        Map<String, Object> result = new HashMap<>();
        result.put("code", 0);
        result.put("message", "success");

        Map<String, Object> data = new HashMap<>();
        data.put("total", 2);
        data.put("list", List.of(
                Map.of("date", "2026-03-18", "rate", 7.21),
                Map.of("date", "2026-03-19", "rate", 7.23)
        ));

        result.put("data", data);
        return result;
    }
}