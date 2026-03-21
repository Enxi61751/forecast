package com.citicup.dto.report;

import com.citicup.entity.RiskReport;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RiskReportResponse {
    private Long id;
    private Long predictionRunId;
    private Instant createdAt;
    private String reportText;
    private String materialsJson;

    public static RiskReportResponse fromEntity(RiskReport r) {
        return RiskReportResponse.builder()
                .id(r.getId())
                .predictionRunId(r.getPredictionRunId())
                .createdAt(r.getCreatedAt())
                .reportText(r.getReportText())
                .materialsJson(r.getMaterialsJson())
                .build();
    }
}
