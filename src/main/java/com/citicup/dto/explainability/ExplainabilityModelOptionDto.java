package com.citicup.dto.explainability;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class ExplainabilityModelOptionDto {
    private String key;
    private String label;

    public ExplainabilityModelOptionDto(String key, String label) {
        this.key = key;
        this.label = label;
    }
}