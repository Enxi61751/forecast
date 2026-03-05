package com.citicup.service;

import com.citicup.dto.predict.PredictRequest;
import com.citicup.dto.predict.PredictResponse;
import com.citicup.entity.PredictionRun;
import com.citicup.repository.PredictionRunRepo;
import com.citicup.service.client.ModelServiceClient;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.Instant;

@Service
@RequiredArgsConstructor
public class PredictService {

    private final ModelServiceClient modelClient;
    private final PredictionRunRepo runRepo;
    private final StringRedisTemplate redis;
    private final ObjectMapper om = new ObjectMapper();

    private static String cacheKey(String target, String horizon) {
        return "pred:latest:" + target + ":" + horizon;
    }

    public PredictResponse runPrediction(PredictRequest req) {
        // 1) call model service
        PredictResponse resp = modelClient.predict(req);

        // 2) persist
        String forecastJson;
        String extremeJson;
        try {
            forecastJson = om.writeValueAsString(resp.getForecast());
            extremeJson = om.writeValueAsString(resp.getExtremeClass());
        } catch (Exception e) {
            throw new RuntimeException("serialize predict response failed: " + e.getMessage());
        }

        PredictionRun saved = runRepo.save(
                PredictionRun.builder()
                        .target(req.getTarget())
                        .horizon(req.getHorizon())
                        .runAt(Instant.now())
                        .forecastJson(forecastJson)
                        .extremeClsJson(extremeJson)
                        .build()
        );

        // 3) cache latest
        redis.opsForValue().set(cacheKey(req.getTarget(), req.getHorizon()), String.valueOf(saved.getId()), Duration.ofMinutes(5));

        return resp;
    }
}