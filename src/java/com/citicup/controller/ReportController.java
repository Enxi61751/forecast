package com.citicup.controller;

import com.citicup.common.ApiResponse;
import com.citicup.service.ReportService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/report")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @PostMapping("/generate/{predictionRunId}")
    public ApiResponse<Long> generate(@PathVariable Long predictionRunId) {
        return ApiResponse.ok(reportService.generateReport(predictionRunId));
    }
}