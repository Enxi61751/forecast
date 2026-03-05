package com.citicup.controller;

import com.citicup.common.ApiResponse;
import com.citicup.dto.predict.PredictRequest;
import com.citicup.dto.predict.PredictResponse;
import com.citicup.service.PredictService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/predict")
@RequiredArgsConstructor
public class PredictController {

    private final PredictService predictService;

    @PostMapping("/run")
    public ApiResponse<PredictResponse> run(@Valid @RequestBody PredictRequest req) {
        return ApiResponse.ok(predictService.runPrediction(req));
    }
}