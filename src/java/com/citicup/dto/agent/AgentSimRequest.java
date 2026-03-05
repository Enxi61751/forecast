package com.citicup.dto.agent;

import lombok.Data;

@Data
public class AgentSimRequest {
    private String target;
    private String horizon;
    private String forecastJson;
}