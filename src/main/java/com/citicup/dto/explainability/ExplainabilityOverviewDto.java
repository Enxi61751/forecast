package com.citicup.dto.explainability;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class ExplainabilityOverviewDto {
    private String modelName;
    private String modelType;
    private Integer trainLag;
    private Integer updatePeriod;
}