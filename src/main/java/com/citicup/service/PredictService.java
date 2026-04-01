package com.citicup.service;

import com.citicup.dto.predict.PredictRequest;
import com.citicup.dto.predict.PredictResponse;
import com.citicup.entity.Event;
import com.citicup.entity.IndicatorDaily;
import com.citicup.entity.OilPriceDailyOhlcv;
import com.citicup.entity.PredictionRun;
import com.citicup.repository.EventRepository;
import com.citicup.repository.IndicatorDailyRepo;
import com.citicup.repository.OilPriceDailyOhlcvRepo;
import com.citicup.repository.PredictionRunRepo;
import com.citicup.service.client.ModelServiceClient;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.logging.Logger;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PredictService {

    private static final Logger logger = Logger.getLogger(PredictService.class.getName());

    private static final int DEFAULT_PRICE_LOOKBACK = 60;
    private static final int DEFAULT_INDICATOR_LOOKBACK = 60;
    private static final int DEFAULT_EVENT_LOOKBACK = 20;

    private final ModelServiceClient modelClient;
    private final PredictionRunRepo runRepo;
    private final StringRedisTemplate redis;
    private final ObjectMapper om;

    private final OilPriceDailyOhlcvRepo oilPriceDailyOhlcvRepo;
    private final IndicatorDailyRepo indicatorDailyRepo;
    private final EventRepository eventRepository;

    private static String cacheKey(String target, String horizon) {
        return "pred:latest:" + target + ":" + horizon;
    }

    public PredictResponse runPrediction(PredictRequest req) {
        Map<String, Object> payload = normalizePayload(req);

        PredictRequest modelReq = new PredictRequest();
        modelReq.setTarget(normalizeTarget(req.getTarget()));
        modelReq.setHorizon(normalizeHorizon(req.getHorizon()));
        modelReq.setAsOf(req.getAsOf());
        modelReq.setPayload(payload);

        logModelRequest(modelReq);

        PredictResponse resp;
        try {
            resp = modelClient.predict(modelReq);
        } catch (Exception e) {
            logger.warning("Model service call failed: " + e.getMessage());
            throw new RuntimeException("Model service unavailable: " + e.getMessage(), e);
        }

        persistRun(req, resp);
        cacheLatest(req);

        return resp;
    }

    private Map<String, Object> normalizePayload(PredictRequest req) {
        Map<String, Object> incoming = req.getPayload() == null
                ? new LinkedHashMap<>()
                : new LinkedHashMap<>(req.getPayload());

        boolean hasSeries = incoming.containsKey("series") && incoming.get("series") != null;
        if (hasSeries) {
            incoming.putIfAbsent("events", Collections.emptyList());
            incoming.putIfAbsent("ceemdan", defaultCeemdanConfig());
            return incoming;
        }

        return buildPayloadFromDatabase(req);
    }

    private Map<String, Object> buildPayloadFromDatabase(PredictRequest req) {
        String modelTarget = normalizeTarget(req.getTarget());
        String dbSymbol = toDbSymbol(modelTarget);

        List<OilPriceDailyOhlcv> priceRows = oilPriceDailyOhlcvRepo.findBySymbolOrderByTradeDateAsc(dbSymbol);

        if (priceRows == null || priceRows.isEmpty()) {
            throw new RuntimeException("No oil price series found for target: " + modelTarget + " (db symbol: " + dbSymbol + ")");
        }

        if (priceRows.size() > DEFAULT_PRICE_LOOKBACK) {
            priceRows = priceRows.subList(priceRows.size() - DEFAULT_PRICE_LOOKBACK, priceRows.size());
        }

        List<Map<String, Object>> priceSeries = priceRows.stream()
                .filter(row -> row.getTradeDate() != null && row.getClosePrice() != null)
                .map(row -> point(toIsoTime(row.getTradeDate()), row.getClosePrice()))
                .collect(Collectors.toList());

        Map<String, Object> series = new LinkedHashMap<>();
        series.put("price", priceSeries);
        series.put("indicators", Collections.emptyMap());
        series.put("sentiment_index", Collections.emptyList());

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("series", series);
        payload.put("events", Collections.emptyList());

        Map<String, Object> ceemdan = new LinkedHashMap<>();
        ceemdan.put("enabled", false);
        payload.put("ceemdan", ceemdan);

        return payload;
    }
    private Map<String, List<Map<String, Object>>> buildIndicatorSeries(List<IndicatorDaily> rows) {
        Map<String, List<Map<String, Object>>> result = new LinkedHashMap<>();
        if (rows.isEmpty()) {
            return result;
        }

        putIndicator(result, "event_count", rows, row -> toDouble(row.getEventCount()));
        putIndicator(result, "pos_count", rows, row -> toDouble(row.getPosCount()));
        putIndicator(result, "neg_count", rows, row -> toDouble(row.getNegCount()));
        putIndicator(result, "sentiment_sum", rows, IndicatorDaily::getSentimentSum);
        putIndicator(result, "sentiment_mean", rows, IndicatorDaily::getSentimentMean);
        putIndicator(result, "max_abs_sentiment", rows, IndicatorDaily::getMaxAbsSentiment);

        return result;
    }

    private List<Map<String, Object>> buildSentimentIndex(List<IndicatorDaily> rows) {
        if (rows.isEmpty()) {
            return Collections.emptyList();
        }

        return rows.stream()
                .filter(row -> row.getSentimentMean() != null)
                .map(row -> point(toIsoTime(row.getDate()), row.getSentimentMean()))
                .collect(Collectors.toList());
    }

    private void putIndicator(
            Map<String, List<Map<String, Object>>> container,
            String key,
            List<IndicatorDaily> rows,
            java.util.function.Function<IndicatorDaily, Double> valueGetter
    ) {
        List<Map<String, Object>> points = rows.stream()
                .map(row -> {
                    Double value = valueGetter.apply(row);
                    if (value == null) return null;
                    return point(toIsoTime(row.getDate()), value);
                })
                .filter(Objects::nonNull)
                .collect(Collectors.toList());

        if (!points.isEmpty()) {
            container.put(key, points);
        }
    }

    private List<Map<String, Object>> buildEvents() {
        List<Event> rows = eventRepository.findAll();
        if (rows == null || rows.isEmpty()) {
            return Collections.emptyList();
        }

        return rows.stream()
                .filter(e -> e.getOccurredAt() != null)
                .sorted(Comparator.comparing(Event::getOccurredAt))
                .skip(Math.max(0, rows.size() - DEFAULT_EVENT_LOOKBACK))
                .map(e -> {
                    Map<String, Object> m = new LinkedHashMap<>();
                    m.put("occurredAt", e.getOccurredAt().toInstant(ZoneOffset.UTC).toString());
                    m.put("eventType", safeString(e.getEventType(), "general"));
                    m.put("intensity", e.getIntensity() == null ? 0.0 : e.getIntensity());
                    if (e.getSummary() != null && !e.getSummary().isBlank()) {
                        m.put("summary", e.getSummary());
                    }
                    return m;
                })
                .collect(Collectors.toList());
    }

    private Map<String, Object> defaultCeemdanConfig() {
        Map<String, Object> ceemdan = new LinkedHashMap<>();
        ceemdan.put("enabled", true);
        ceemdan.put("trials", 100);
        ceemdan.put("noise_width", 0.2);
        ceemdan.put("max_imfs", 8);
        return ceemdan;
    }

    private void persistRun(PredictRequest req, PredictResponse resp) {
        String forecastJson;
        String extremeJson;
        try {
            forecastJson = om.writeValueAsString(resp.getForecast());
            extremeJson = om.writeValueAsString(resp.getExtremeClass());
        } catch (Exception e) {
            throw new RuntimeException("serialize predict response failed: " + e.getMessage(), e);
        }

        runRepo.save(
                PredictionRun.builder()
                        .target(req.getTarget())
                        .horizon(req.getHorizon())
                        .runAt(Instant.now())
                        .forecastJson(forecastJson)
                        .extremeClsJson(extremeJson)
                        .build()
        );
    }

    private void cacheLatest(PredictRequest req) {
        try {
            redis.opsForValue().set(
                    cacheKey(req.getTarget(), req.getHorizon()),
                    String.valueOf(Instant.now().toEpochMilli()),
                    Duration.ofMinutes(5)
            );
        } catch (Exception e) {
            logger.warning("Redis cache failed (non-critical): " + e.getMessage());
        }
    }

    private void logModelRequest(PredictRequest req) {
        try {
            Map<String, Object> body = new LinkedHashMap<>();
            if (req.getPayload() != null) {
                body.putAll(req.getPayload());
            }
            body.put("target", req.getTarget());
            body.put("horizon", req.getHorizon());
            if (req.getAsOf() != null) {
                body.put("asOf", req.getAsOf().toString());
            }
            logger.info("Predict request body to model = " + om.writeValueAsString(body));
        } catch (Exception e) {
            logger.warning("Failed to log predict request body: " + e.getMessage());
        }
    }

    private String normalizeTarget(String target) {
        if (target == null || target.isBlank()) return "WTI";
        String t = target.trim().toUpperCase(Locale.ROOT);
        if ("WTI_USD".equals(t)) return "WTI";
        if ("BRENT_USD".equals(t)) return "BRENT";
        if ("LCO1".equals(t)) return "BRENT";
        if ("CL1".equals(t)) return "WTI";
        return t;
    }

    private String toDbSymbol(String target) {
        String t = normalizeTarget(target);
        if ("BRENT".equals(t)) return "LCO1";
        if ("WTI".equals(t)) return "CL1";
        return t;
    }

    private String normalizeHorizon(String horizon) {
        if (horizon == null || horizon.isBlank()) {
            return "1d";
        }
        String h = horizon.trim().toLowerCase(Locale.ROOT);
        if (h.matches("\\d+")) {
            return h + "d";
        }
        return h;
    }

    private Map<String, Object> point(String t, Double v) {
        Map<String, Object> p = new LinkedHashMap<>();
        p.put("t", t);
        p.put("v", v);
        return p;
    }

    private String toIsoTime(LocalDate date) {
        return DateTimeFormatter.ISO_INSTANT.format(date.atStartOfDay().toInstant(ZoneOffset.UTC));
    }

    private String safeString(String v, String fallback) {
        return (v == null || v.isBlank()) ? fallback : v;
    }

    private Double toDouble(Integer value) {
        return value == null ? null : value.doubleValue();
    }
}