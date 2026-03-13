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

        // 这里先用模板拼接；后续你们可接 LLM 来写更自然的报告
        String reportText = """
                【油价风险快报】
                标的：%s
                期限：%s
                运行时间：%s

                1) 预测结论：见系统预测曲线/区间
                2) 极端情景：见极端分类模块输出
                3) 解释材料（多智能体）：见附录材料
                """.formatted(run.getTarget(), run.getHorizon(), run.getRunAt());

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
}
