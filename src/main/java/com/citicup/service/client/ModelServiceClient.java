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

    @Value("${app.agent-service.base-url}")
    private String agentBaseUrl;

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
        // Build stagex2 SingleStepRequest from prediction context
        // factor_snapshot
        Map<String, Object> factorSnapshot = new HashMap<>();
        factorSnapshot.put("trend_score", 0.0);
        factorSnapshot.put("rsi_status", "Neutral");
        factorSnapshot.put("term_structure", "Contango");

        // tail_risk_report
        Map<String, Object> tailRisk = new HashMap<>();
        tailRisk.put("gamma_profile", "Neutral");
        tailRisk.put("liquidity_stress", 0.3);

        // market_microstructure
        Map<String, Object> microstructure = new HashMap<>();
        microstructure.put("bid_ask_spread", 0.05);
        microstructure.put("order_book_depth", "Normal");

        // session_info
        Map<String, Object> sessionInfo = new HashMap<>();
        sessionInfo.put("phase", "Mid-Day");
        sessionInfo.put("time_to_close", 240);

        // environment
        Map<String, Object> environment = new HashMap<>();
        environment.put("factor_snapshot", factorSnapshot);
        environment.put("tail_risk_report", tailRisk);
        environment.put("market_microstructure", microstructure);
        environment.put("session_info", sessionInfo);

        // event — derive headline/body from prediction data
        String forecastBody = req.getForecastJson() != null ? req.getForecastJson() : "No forecast data";
        Map<String, Object> event = new HashMap<>();
        event.put("headline", String.format("Oil price forecast: %s over %s", req.getTarget(), req.getHorizon()));
        event.put("body", forecastBody.length() > 1000 ? forecastBody.substring(0, 1000) : forecastBody);
        event.put("source", "CitiCup Model");
        event.put("impact_type", "price");
        event.put("sentiment_score", 0.0);

        // self_state — CTA archetype as default agent template
        Map<String, Object> selfState = new HashMap<>();
        selfState.put("role", "CTA");
        selfState.put("mandate", "trend-following momentum strategy");
        selfState.put("hedger_type", "neutral");
        selfState.put("max_leverage", 3.0);
        selfState.put("stop_loss_pct", 0.05);
        selfState.put("position", 0.0);
        selfState.put("unrealized_pnl", 0.0);
        selfState.put("unrealized_pnl_pct", 0.0);
        selfState.put("cash_level", 1000000.0);
        selfState.put("last_action", "NONE");
        selfState.put("consecutive_losses", 0);
        selfState.put("view_history", "neutral");

        // simulation_input — note stagex2 uses alias "self" for self_state
        Map<String, Object> simulationInput = new HashMap<>();
        simulationInput.put("environment", environment);
        simulationInput.put("event", event);
        simulationInput.put("self", selfState);

        // top-level SingleStepRequest — note stagex2 uses alias "input" for simulation_input
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("input", simulationInput);
        requestBody.put("current_price", 80.0);
        requestBody.put("current_volatility", 0.2);
        requestBody.put("dealer_inventory", 100);

        return restClient.post()
                .uri(agentBaseUrl + "/simulate/single")
                .body(requestBody)
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