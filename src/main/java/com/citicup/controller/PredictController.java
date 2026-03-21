package com.citicup.controller;

import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class PredictController {

    @PostMapping("/api/predict")
    public Map<String, Object> predict(@RequestBody Map<String, Object> payload) {
        Object modelType = payload.get("modelType");

        Map<String, Object> result = new HashMap<>();
        result.put("code", 0);
        result.put("message", "success");

        Map<String, Object> data = new HashMap<>();
        data.put("modelType", modelType == null ? "unknown" : modelType.toString());
        data.put("result", List.of(
                Map.of("date", "2026-04-01", "value", 7.68),
                Map.of("date", "2026-05-01", "value", 7.72)
        ));

        result.put("data", data);
        return result;
    }
}