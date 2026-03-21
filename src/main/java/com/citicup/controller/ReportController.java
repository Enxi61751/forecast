package com.citicup.controller;

import com.citicup.common.ApiResponse;
import com.citicup.dto.report.RiskReportResponse;
import com.citicup.service.ReportService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/report")
public class ReportController {

    private final ReportService reportService;

    public ReportController(ReportService reportService) {
        this.reportService = reportService;
    }

    /**
     * Query 形式：GET/POST /api/report/generate?predictionRunId=1
     * 兼容误传的引号（如 1%22 → 1"），会剥离后再解析为 Long。
     */
    @GetMapping("/generate")
    public ApiResponse<RiskReportResponse> generateByQueryGet(
            @RequestParam("predictionRunId") String predictionRunIdRaw) {
        return generate(parsePredictionRunId(predictionRunIdRaw));
    }

    @PostMapping("/generate")
    public ApiResponse<RiskReportResponse> generateByQueryPost(
            @RequestParam("predictionRunId") String predictionRunIdRaw) {
        return generate(parsePredictionRunId(predictionRunIdRaw));
    }

    /**
     * 路径形式：GET/POST /api/report/generate/1（与部分前端/测试一致）
     */
    @GetMapping("/generate/{predictionRunId}")
    public ApiResponse<RiskReportResponse> generateByPathGet(@PathVariable Long predictionRunId) {
        return generate(predictionRunId);
    }

    @PostMapping("/generate/{predictionRunId}")
    public ApiResponse<RiskReportResponse> generateByPathPost(@PathVariable Long predictionRunId) {
        return generate(predictionRunId);
    }

    private ApiResponse<RiskReportResponse> generate(Long predictionRunId) {
        return ApiResponse.ok(RiskReportResponse.fromEntity(reportService.generateReport(predictionRunId)));
    }

    private static Long parsePredictionRunId(String raw) {
        if (raw == null || raw.isBlank()) {
            throw new IllegalArgumentException("predictionRunId is required");
        }
        String s = raw.trim().replace("\"", "").replace("'", "").trim();
        try {
            return Long.parseLong(s);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("invalid predictionRunId: " + raw);
        }
    }
}
