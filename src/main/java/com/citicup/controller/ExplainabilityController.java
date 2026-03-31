package com.citicup.controller;

import com.citicup.common.ApiResponse;
import com.citicup.dto.explainability.ExplainabilityModelOptionDto;
import com.citicup.dto.explainability.ExplainabilityRecordDto;
import com.citicup.dto.explainability.ExplainabilityResponseDto;
import com.citicup.service.ExplainabilityService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/explainability")
@RequiredArgsConstructor
public class ExplainabilityController {

    private final ExplainabilityService explainabilityService;

    @GetMapping("/models")
    public ApiResponse<List<ExplainabilityModelOptionDto>> getModelOptions() {
        return ApiResponse.ok(explainabilityService.listModels());
    }

    @GetMapping("/{modelKey}")
    public ApiResponse<ExplainabilityResponseDto> getByModelKey(@PathVariable String modelKey) {
        return ApiResponse.ok(explainabilityService.getByModelKey(modelKey));
    }

    @GetMapping("/{modelKey}/{trainDate}")
    public ApiResponse<ExplainabilityRecordDto> getRecord(
            @PathVariable String modelKey,
            @PathVariable String trainDate
    ) {
        return ApiResponse.ok(explainabilityService.getRecord(modelKey, trainDate));
    }
}