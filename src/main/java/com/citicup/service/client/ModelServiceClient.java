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
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
@RequiredArgsConstructor
public class ModelServiceClient {

    private final RestClient restClient;

    @Value("${app.model-service.base-url}")
    private String baseUrl;

    @Value("${app.llm.api-key}")
    private String llmApiKey;

    @Value("${app.llm.url}")
    private String llmUrl;

    public SentimentResponse scoreNews(NewsIngestRequest req) {
        return restClient.post()
                .uri(baseUrl + "/sentiment/score")
                .body(req)
                .retrieve()
                .body(SentimentResponse.class);
    }

    public PredictResponse predict(PredictRequest req) {
        // 将 payload 内容展开到顶层，与 target/horizon/asOf 合并，匹配模型 API 结构
        Map<String, Object> modelReq = new HashMap<>(req.getPayload());
        modelReq.put("target", req.getTarget());
        modelReq.put("horizon", req.getHorizon());
        if (req.getAsOf() != null) {
            modelReq.put("asOf", req.getAsOf().toString());
        }
        return restClient.post()
                .uri(baseUrl + "/predict")
                .body(modelReq)
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

    @SuppressWarnings("unchecked")
    public String callLlm(String prompt) {
        Map<String, Object> requestBody = Map.of(
                "model", "deepseek-reasoner",
                "messages", List.of(
                        Map.of("role", "user", "content", prompt)
                )
        );

        Map<String, Object> response = restClient.post()
                .uri(llmUrl)
                .header("Authorization", "Bearer " + llmApiKey)
                .header("Content-Type", "application/json")
                .body(requestBody)
                .retrieve()
                .body(Map.class);

        if (response == null) {
            throw new RuntimeException("LLM returned empty response");
        }
        List<Map<String, Object>> choices = (List<Map<String, Object>>) response.get("choices");
        if (choices == null || choices.isEmpty()) {
            throw new RuntimeException("LLM response missing choices: " + response);
        }
        Map<String, Object> message = (Map<String, Object>) choices.get(0).get("message");
        if (message == null) {
            throw new RuntimeException("LLM response missing message in choices[0]");
        }
        String content = (String) message.get("content");
        if (content == null) {
            throw new RuntimeException("LLM response missing content in message");
        }
        return content;
    }
}