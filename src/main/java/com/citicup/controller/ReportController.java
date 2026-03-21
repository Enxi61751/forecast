package com.citicup.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class ReportController {

    @GetMapping("/api/report/list")
    public Map<String, Object> list() {
        Map<String, Object> result = new HashMap<>();
        result.put("code", 0);
        result.put("message", "success");

        Map<String, Object> data = new HashMap<>();
        data.put("total", 1);
        data.put("list", List.of(
                Map.of("id", 1, "title", "Weekly Report", "type", "summary")
        ));

        result.put("data", data);
        return result;
    }
}