package com.citicup.dto.explainability;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class ExplainabilityRecordDto {
    private String trainDate;
    private Integer sampleCount;
    private Double bestCvScore;
    private Map<String, Object> bestParams = new LinkedHashMap<>();
    private String summaryPlot;
    private String barPlot;
    private List<ExplainabilityTopFeatureDto> topFeatures = new ArrayList<>();
    private String conclusion;
}