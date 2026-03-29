package com.citicup.service.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.citicup.dto.agent.Stage2SingleRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class Stage2AgentClient {

    private final RestTemplate restTemplate;
    private final String baseUrl;

    public Stage2AgentClient(
            RestTemplateBuilder builder,
            @Value("${stage2.base-url}") String baseUrl
    ) {
        this.restTemplate = builder.build();
        this.baseUrl = baseUrl;
    }

    public JsonNode simulateSingle(Stage2SingleRequest request) {
        String url = baseUrl + "/simulate/single";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<Stage2SingleRequest> entity = new HttpEntity<>(request, headers);

        ResponseEntity<JsonNode> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                entity,
                JsonNode.class
        );

        return response.getBody();
    }

    public JsonNode healthz() {
        String url = baseUrl + "/healthz";
        return restTemplate.getForObject(url, JsonNode.class);
    }
}