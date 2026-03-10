package com.citicup.service.client;

import com.citicup.dto.agent.AgentSimRequest;
import com.citicup.dto.news.NewsIngestRequest;
import com.citicup.dto.news.SentimentResponse;
import com.citicup.dto.predict.PredictRequest;
import com.citicup.dto.predict.PredictResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
@RequiredArgsConstructor
public class ModelServiceClient {

    private final RestClient restClient;

    @Value("${app.model-service.base-url}")
    private String baseUrl;

    public SentimentResponse scoreNews(NewsIngestRequest req) {
        return restClient.post()
                .uri(baseUrl + "/sentiment/score")
                .body(req)
                .retrieve()
                .body(SentimentResponse.class);
    }

    public PredictResponse predict(PredictRequest req) {
        return restClient.post()
                .uri(baseUrl + "/predict")
                .body(req)
                .retrieve()
                .body(PredictResponse.class);
    }

    public String simulateAgents(AgentSimRequest req) {
        return restClient.post()
                .uri(baseUrl + "/agents/simulate")
                .body(req)
                .retrieve()
                .body(String.class);
    }
}