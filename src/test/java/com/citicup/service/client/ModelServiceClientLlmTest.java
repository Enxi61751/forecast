package com.citicup.service.client;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Answers;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestClient;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ModelServiceClientLlmTest {

    private RestClient.ResponseSpec responseSpec;
    private ModelServiceClient client;

    @BeforeEach
    void setUp() {
        // RETURNS_SELF 让所有 builder 链方法（uri/header/body）返回同一个 mock 自身，
        // 只需单独 mock retrieve()（返回类型不同）
        RestClient.RequestBodyUriSpec uriSpec =
                mock(RestClient.RequestBodyUriSpec.class, Answers.RETURNS_SELF);
        responseSpec = mock(RestClient.ResponseSpec.class);
        lenient().when(uriSpec.retrieve()).thenReturn(responseSpec);

        RestClient restClient = mock(RestClient.class);
        when(restClient.post()).thenReturn(uriSpec);

        client = new ModelServiceClient(restClient);
        ReflectionTestUtils.setField(client, "baseUrl", "http://localhost:8000");
        ReflectionTestUtils.setField(client, "llmApiKey", "test-key");
        ReflectionTestUtils.setField(client, "llmUrl", "https://api.test.com/completions");
    }

    @Test
    void callLlm_normalResponse_returnsContent() {
        Map<String, Object> message = Map.of("role", "assistant", "content", "油价风险分析内容");
        Map<String, Object> choice = Map.of("message", message);
        when(responseSpec.body(Map.class)).thenReturn(Map.of("choices", List.of(choice)));

        assertEquals("油价风险分析内容", client.callLlm("测试 prompt"));
    }

    @Test
    void callLlm_nullResponse_throwsWithClearMessage() {
        when(responseSpec.body(Map.class)).thenReturn(null);

        RuntimeException ex = assertThrows(RuntimeException.class, () -> client.callLlm("test"));
        assertTrue(ex.getMessage().contains("LLM returned empty response"), ex.getMessage());
    }

    @Test
    void callLlm_missingChoicesKey_throwsWithClearMessage() {
        when(responseSpec.body(Map.class)).thenReturn(Map.of("id", "xyz"));

        RuntimeException ex = assertThrows(RuntimeException.class, () -> client.callLlm("test"));
        assertTrue(ex.getMessage().contains("missing choices"), ex.getMessage());
    }

    @Test
    void callLlm_emptyChoicesList_throwsWithClearMessage() {
        when(responseSpec.body(Map.class)).thenReturn(Map.of("choices", List.of()));

        RuntimeException ex = assertThrows(RuntimeException.class, () -> client.callLlm("test"));
        assertTrue(ex.getMessage().contains("missing choices"), ex.getMessage());
    }

    @Test
    void callLlm_nullMessage_throwsWithClearMessage() {
        Map<String, Object> choice = new HashMap<>();
        choice.put("message", null);
        when(responseSpec.body(Map.class)).thenReturn(Map.of("choices", List.of(choice)));

        RuntimeException ex = assertThrows(RuntimeException.class, () -> client.callLlm("test"));
        assertTrue(ex.getMessage().contains("missing message"), ex.getMessage());
    }

    @Test
    void callLlm_nullContent_throwsWithClearMessage() {
        Map<String, Object> message = new HashMap<>();
        message.put("content", null);
        Map<String, Object> choice = Map.of("message", message);
        when(responseSpec.body(Map.class)).thenReturn(Map.of("choices", List.of(choice)));

        RuntimeException ex = assertThrows(RuntimeException.class, () -> client.callLlm("test"));
        assertTrue(ex.getMessage().contains("missing content"), ex.getMessage());
    }
}
