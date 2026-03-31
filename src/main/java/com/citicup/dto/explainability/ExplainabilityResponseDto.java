package com.citicup.dto.explainability;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class ExplainabilityResponseDto {
    private ExplainabilityOverviewDto overview;
    private List<ExplainabilityRecordDto> records = new ArrayList<>();
}