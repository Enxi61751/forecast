package com.citicup.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
public class HealthController {

    @GetMapping("/api/health")
    public Map<String, Object> health() {
        Map<String, Object> result = new HashMap<>();
        result.put("code", 0);
        result.put("message", "success");

        Map<String, Object> data = new HashMap<>();
        data.put("status", "UP");
        data.put("time", LocalDateTime.now().toString());

        result.put("data", data);
        return result;
    }
}