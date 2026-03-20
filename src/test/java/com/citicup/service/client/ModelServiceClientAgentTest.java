package com.citicup.service.client;

import com.citicup.dto.agent.AgentSimRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Answers;
import org.mockito.ArgumentCaptor;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestClient;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Tests that ModelServiceClient.simulateAgents() sends the correct request
 * to the stagex2 agent service at /simulate/single (not the old /agents/simulate).
 */
@ExtendWith(MockitoExtension.class)
class ModelServiceClientAgentTest {

    private RestClient.RequestBodyUriSpec uriSpec;
    private RestClient.ResponseSpec responseSpec;
    private ModelServiceClient client;

    @BeforeEach
    void setUp() {
        uriSpec = mock(RestClient.RequestBodyUriSpec.class, Answers.RETURNS_SELF);
        responseSpec = mock(RestClient.ResponseSpec.class);
        lenient().when(uriSpec.retrieve()).thenReturn(responseSpec);

        RestClient restClient = mock(RestClient.class);
        when(restClient.post()).thenReturn(uriSpec);

        client = new ModelServiceClient(restClient);
        ReflectionTestUtils.setField(client, "baseUrl", "http://localhost:8000");
        ReflectionTestUtils.setField(client, "agentBaseUrl", "http://localhost:8001");
        ReflectionTestUtils.setField(client, "llmApiKey", "test-key");
        ReflectionTestUtils.setField(client, "llmUrl", "https://api.test.com/completions");
    }

    // ── helpers ──────────────────────────────────────────────────────────────

    private AgentSimRequest buildReq() {
        AgentSimRequest r = new AgentSimRequest();
        r.setTarget("WTI");
        r.setHorizon("7d");
        r.setForecastJson("{\"point\":[{\"t\":\"2026-03-21T00:00:00Z\",\"v\":80.5}]}");
        return r;
    }

    // ── 1. Correct URL ────────────────────────────────────────────────────────

    @Test
    void simulateAgents_callsAgentServiceAtCorrectPath() {
        when(responseSpec.body(String.class)).thenReturn("{\"market\":{}}");

        client.simulateAgents(buildReq());

        verify(uriSpec).uri("http://localhost:8001/simulate/single");
    }

    @Test
    void simulateAgents_doesNotCallOldLegacyPath() {
        when(responseSpec.body(String.class)).thenReturn("{}");

        client.simulateAgents(buildReq());

        // must never call the old /agents/simulate path on the model service
        verify(uriSpec, never()).uri("http://localhost:8000/agents/simulate");
    }

    // ── 2. Request body top-level structure ───────────────────────────────────

    @Test
    @SuppressWarnings("unchecked")
    void simulateAgents_requestBodyHasRequiredTopLevelKeys() {
        when(responseSpec.body(String.class)).thenReturn("{}");
        ArgumentCaptor<Object> bodyCaptor = ArgumentCaptor.forClass(Object.class);

        client.simulateAgents(buildReq());

        verify(uriSpec).body(bodyCaptor.capture());
        Map<String, Object> body = (Map<String, Object>) bodyCaptor.getValue();

        // stagex2 SingleStepRequest top-level fields
        assertTrue(body.containsKey("input"),              "must have 'input' (stagex2 alias for simulation_input)");
        assertTrue(body.containsKey("current_price"),      "must have 'current_price'");
        assertTrue(body.containsKey("current_volatility"), "must have 'current_volatility'");
        assertTrue(body.containsKey("dealer_inventory"),   "must have 'dealer_inventory'");
    }

    // ── 3. SimulationInput inner structure ────────────────────────────────────

    @Test
    @SuppressWarnings("unchecked")
    void simulateAgents_inputContainsEnvironmentEventAndSelf() {
        when(responseSpec.body(String.class)).thenReturn("{}");
        ArgumentCaptor<Object> bodyCaptor = ArgumentCaptor.forClass(Object.class);

        client.simulateAgents(buildReq());
        verify(uriSpec).body(bodyCaptor.capture());

        Map<String, Object> input = (Map<String, Object>)
                ((Map<String, Object>) bodyCaptor.getValue()).get("input");

        assertTrue(input.containsKey("environment"), "simulation_input must have 'environment'");
        assertTrue(input.containsKey("event"),       "simulation_input must have 'event'");
        // stagex2 uses alias "self" (not "self_state") for SelfState
        assertTrue(input.containsKey("self"),        "simulation_input must use alias 'self' for self_state");
    }

    @Test
    @SuppressWarnings("unchecked")
    void simulateAgents_environmentHasRequiredSubFields() {
        when(responseSpec.body(String.class)).thenReturn("{}");
        ArgumentCaptor<Object> bodyCaptor = ArgumentCaptor.forClass(Object.class);

        client.simulateAgents(buildReq());
        verify(uriSpec).body(bodyCaptor.capture());

        Map<String, Object> input = (Map<String, Object>)
                ((Map<String, Object>) bodyCaptor.getValue()).get("input");
        Map<String, Object> env = (Map<String, Object>) input.get("environment");

        assertTrue(env.containsKey("factor_snapshot"),     "environment missing factor_snapshot");
        assertTrue(env.containsKey("tail_risk_report"),    "environment missing tail_risk_report");
        assertTrue(env.containsKey("market_microstructure"), "environment missing market_microstructure");
        assertTrue(env.containsKey("session_info"),        "environment missing session_info");
    }

    // ── 4. Event body carries forecast data ───────────────────────────────────

    @Test
    @SuppressWarnings("unchecked")
    void simulateAgents_eventBodyContainsForecastJson() {
        when(responseSpec.body(String.class)).thenReturn("{}");
        ArgumentCaptor<Object> bodyCaptor = ArgumentCaptor.forClass(Object.class);

        AgentSimRequest req = buildReq();
        req.setForecastJson("{\"point\":[{\"v\":82.0}]}");
        client.simulateAgents(req);
        verify(uriSpec).body(bodyCaptor.capture());

        Map<String, Object> input = (Map<String, Object>)
                ((Map<String, Object>) bodyCaptor.getValue()).get("input");
        Map<String, Object> event = (Map<String, Object>) input.get("event");

        assertTrue(event.get("body").toString().contains("82.0"),
                "event.body should contain forecast data");
    }

    // ── 5. Long forecastJson is truncated ─────────────────────────────────────

    @Test
    @SuppressWarnings("unchecked")
    void simulateAgents_forecastJsonLongerThan1000Chars_isTruncated() {
        when(responseSpec.body(String.class)).thenReturn("{}");
        ArgumentCaptor<Object> bodyCaptor = ArgumentCaptor.forClass(Object.class);

        AgentSimRequest req = buildReq();
        req.setForecastJson("x".repeat(2000));
        client.simulateAgents(req);
        verify(uriSpec).body(bodyCaptor.capture());

        Map<String, Object> input = (Map<String, Object>)
                ((Map<String, Object>) bodyCaptor.getValue()).get("input");
        Map<String, Object> event = (Map<String, Object>) input.get("event");

        int bodyLen = event.get("body").toString().length();
        assertTrue(bodyLen <= 1000, "forecastJson > 1000 chars must be truncated, got " + bodyLen);
    }

    // ── 6. Null forecastJson falls back to default text ───────────────────────

    @Test
    @SuppressWarnings("unchecked")
    void simulateAgents_nullForecastJson_usesDefaultText() {
        when(responseSpec.body(String.class)).thenReturn("{}");
        ArgumentCaptor<Object> bodyCaptor = ArgumentCaptor.forClass(Object.class);

        AgentSimRequest req = buildReq();
        req.setForecastJson(null);
        client.simulateAgents(req);
        verify(uriSpec).body(bodyCaptor.capture());

        Map<String, Object> input = (Map<String, Object>)
                ((Map<String, Object>) bodyCaptor.getValue()).get("input");
        Map<String, Object> event = (Map<String, Object>) input.get("event");

        String body = event.get("body").toString();
        assertNotNull(body);
        assertFalse(body.isBlank(), "event.body must not be empty when forecastJson is null");
    }

    // ── 7. Response is returned as-is ─────────────────────────────────────────

    @Test
    void simulateAgents_returnsAgentServiceResponse() {
        String expected = "{\"market\":{\"new_price\":81.5},\"agents\":{}}";
        when(responseSpec.body(String.class)).thenReturn(expected);

        String result = client.simulateAgents(buildReq());

        assertEquals(expected, result);
    }
}
