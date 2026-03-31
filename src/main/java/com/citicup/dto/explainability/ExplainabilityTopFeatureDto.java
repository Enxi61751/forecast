package com.citicup.dto.explainability;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class ExplainabilityTopFeatureDto {
    private String name;
    private Double importance;
}