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

@Service
@RequiredArgsConstructor
public class ReportService {

    private final PredictionRunRepo runRepo;
    private final RiskReportRepo reportRepo;
    private final ModelServiceClient modelClient;

    public Long generateReport(Long predictionRunId) {
        PredictionRun run = runRepo.findById(predictionRunId)
                .orElseThrow(() -> new RuntimeException("predictionRun not found"));

        // 调多智能体模拟（解释材料）
        AgentSimRequest simReq = new AgentSimRequest();
        simReq.setTarget(run.getTarget());
        simReq.setHorizon(run.getHorizon());
        simReq.setForecastJson(run.getForecastJson());
        String materialsJson = modelClient.simulateAgents(simReq);

        String prompt = """
                你是一位专业的大宗商品风险分析师，请根据以下数据，用中文撰写一份面向银行风控团队的油价风险快报。

                【预测基本信息】
                - 标的：%s
                - 期限：%s
                - 分析时间：%s

                【量化预测结果】
                %s

                【极端情景分类】
                %s

                【多智能体分析材料】
                %s

                请输出一份结构清晰、语言专业的风险快报，包含：预测结论、风险提示、极端情景说明、主要驱动因素。
                """.formatted(
                        run.getTarget(),
                        run.getHorizon(),
                        run.getRunAt(),
                        run.getForecastJson(),
                        run.getExtremeClsJson(),
                        materialsJson
                );

        String reportText = modelClient.callLlm(prompt);

        RiskReport saved = reportRepo.save(
                RiskReport.builder()
                        .predictionRunId(run.getId())
                        .createdAt(Instant.now())
                        .reportText(reportText)
                        .materialsJson(materialsJson)
                        .build()
        );

        return saved.getId();
    }
    public RiskReport getLatestReport() {
    return reportRepo.findTopByOrderByPredictionRunIdDesc()
            .orElseThrow(() -> new RuntimeException("no reports"));
}
}
