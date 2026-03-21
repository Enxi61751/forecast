package com.citicup.controller;

import com.citicup.common.ApiResponse;
import com.citicup.dto.predict.PredictRequest;
import com.citicup.dto.predict.PredictResponse;
import com.citicup.service.PredictService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/predict")
public class PredictController {

    private final PredictService predictService;

    public PredictController(PredictService predictService) {
        this.predictService = predictService;
    }

    /**
     * 浏览器地址栏访问为 GET；预测实际需 POST + JSON。此处返回说明，避免误以为服务不可用。
     */
    @GetMapping
    public ApiResponse<Map<String, String>> usage() {
        Map<String, String> hint = new LinkedHashMap<>();
        hint.put("message", "预测请使用 POST，Content-Type: application/json");
        hint.put("paths", "POST /api/predict 或 POST /api/predict/run");
        hint.put("exampleBody", "{\"target\":\"WTI\",\"horizon\":\"7d\",\"payload\":{}}");
        return ApiResponse.ok(hint);
    }

    @PostMapping(value = {"", "/run"})
    public ApiResponse<PredictResponse> predict(@Valid @RequestBody PredictRequest request) {
        PredictResponse response = predictService.runPrediction(request);
        return ApiResponse.ok(response);
    }
}