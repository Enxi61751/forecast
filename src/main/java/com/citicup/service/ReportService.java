package com.citicup.service;

import com.citicup.dto.agent.AgentSimRequest;
import com.citicup.entity.PredictionRun;
import com.citicup.entity.RiskReport;
import com.citicup.repository.PredictionRunRepo;
import com.citicup.repository.RiskReportRepo;
import com.citicup.service.client.ModelServiceClient;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Optional;
import java.util.logging.Logger;

@Service
@RequiredArgsConstructor
public class ReportService {

    private static final Logger logger = Logger.getLogger(ReportService.class.getName());

    private final PredictionRunRepo runRepo;
    private final RiskReportRepo reportRepo;
    private final ModelServiceClient modelClient;

    public RiskReport generateReport(Long predictionRunId) {
        PredictionRun run = runRepo.findById(predictionRunId)
                .orElseThrow(() -> new RuntimeException("predictionRun not found"));

        String materialsJson;
        try {
            AgentSimRequest simReq = new AgentSimRequest();
            simReq.setTarget(run.getTarget());
            simReq.setHorizon(run.getHorizon());
            simReq.setForecastJson(run.getForecastJson());
            materialsJson = modelClient.simulateAgents(simReq);
        } catch (Exception e) {
            logger.warning("Agent simulation failed, using mock materials: " + e.getMessage());
            materialsJson = getMockMaterialsJson(run);
        }

        String reportText;
        try {
            reportText = modelClient.generateReport("Oil price risk analysis report for " + run.getTarget());
        } catch (Exception e) {
            logger.warning("LLM report generation failed, using mock report: " + e.getMessage());
            reportText = getMockReportText(run);
        }

        // DB 唯一约束 unique_prediction：每个 prediction_run 仅一条报告；重复生成则更新同一条
        Optional<RiskReport> existingOpt = reportRepo.findByPredictionRunId(predictionRunId);
        RiskReport report;
        if (existingOpt.isPresent()) {
            RiskReport existing = existingOpt.get();
            existing.setReportText(reportText);
            existing.setMaterialsJson(materialsJson);
            existing.setCreatedAt(Instant.now());
            report = existing;
        } else {
            report = RiskReport.builder()
                    .predictionRunId(predictionRunId)
                    .createdAt(Instant.now())
                    .reportText(reportText)
                    .materialsJson(materialsJson)
                    .build();
        }

        return reportRepo.save(report);
    }

    public RiskReport getLatestReport() {
        return reportRepo.findTopByOrderByPredictionRunIdDesc()
                .orElseThrow(() -> new RuntimeException("no reports"));
    }

    private String getMockMaterialsJson(PredictionRun run) {
        return "{\"agents\":[{\"agent\":\"fundamental_analysis\",\"conclusion\":\"Oil fundamentals support higher prices\"},{\"agent\":\"technical_analysis\",\"conclusion\":\"Uptrend remains intact\"}]}";
    }

    private String getMockReportText(PredictionRun run) {
        return String.format("Oil Price Risk Report - %s (%s)%nAnalysis Time: %s%nForecast: %s%n%nConclusion: Oil prices expected to remain stable with upside bias.%nRisk Factors: Geopolitical risks, USD strength, economic slowdown.", 
                run.getTarget(), run.getHorizon(), Instant.now(), run.getForecastJson());
    }
}
