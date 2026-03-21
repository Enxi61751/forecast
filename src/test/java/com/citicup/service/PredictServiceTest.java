package com.citicup.service;

import com.citicup.dto.predict.PredictRequest;
import com.citicup.dto.predict.PredictResponse;
import com.citicup.entity.PredictionRun;
import com.citicup.repository.PredictionRunRepo;
import com.citicup.service.client.ModelServiceClient;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Spy;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

import java.time.Duration;
import java.time.Instant;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PredictServiceTest {

    @Mock ModelServiceClient modelClient;
    @Mock PredictionRunRepo runRepo;
    @Mock StringRedisTemplate redis;
    @Mock ValueOperations<String, String> valueOps;
    @Spy ObjectMapper objectMapper = new ObjectMapper();
    @InjectMocks PredictService predictService;

    @Test
    void runPrediction_callsModelAndSavesRun() {
        PredictRequest req = new PredictRequest();
        req.setTarget("WTI");
        req.setHorizon("1d");
        req.setPayload(Map.of("k", "v"));
        req.setAsOf(Instant.now());

        PredictResponse mockResp = new PredictResponse();
        mockResp.setForecast("forecastData");
        mockResp.setExtremeClass("extremeData");

        PredictionRun savedRun = PredictionRun.builder()
                .id(42L).target("WTI").horizon("1d")
                .runAt(Instant.now())
                .forecastJson("\"forecastData\"")
                .extremeClsJson("\"extremeData\"")
                .build();

        when(modelClient.predict(req)).thenReturn(mockResp);
        when(runRepo.save(any())).thenReturn(savedRun);
        when(redis.opsForValue()).thenReturn(valueOps);

        PredictResponse result = predictService.runPrediction(req);

        assertNotNull(result);
        assertEquals("forecastData", result.getForecast());
        verify(runRepo).save(any(PredictionRun.class));
        verify(valueOps).set(eq("pred:latest:WTI:1d"), eq("42"), any(Duration.class));
    }
}
