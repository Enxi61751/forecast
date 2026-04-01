package com.citicup.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class ExchangeService {

    private static final String WTI_CODE = "WTI_USD";
    private static final String BRENT_CODE = "BRENT_CRUDE_USD";

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    @Value("${app.oilprice.api.url}")
    private String oilApiUrl;

    @Value("${app.oilprice.api.token:}")
    private String oilApiToken;

    public Map<String, Object> getExchangeList() {
        List<Map<String, Object>> list = new ArrayList<>();
        list.add(buildExchangeItem(WTI_CODE));
        list.add(buildExchangeItem(BRENT_CODE));

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("list", list);
        result.put("total", list.size());
        return result;
    }

    private Map<String, Object> buildExchangeItem(String code) {
        JsonNode root = queryOilApi(code);

        JsonNode dataNode = root.path("data");
        if (dataNode.isMissingNode() || dataNode.isNull()) {
            throw new RuntimeException("Oil API response missing data field for code=" + code);
        }

        BigDecimal latestPrice = toBigDecimal(dataNode.path("price").asText("0"));
        String latestTime = formatTime(dataNode.path("created_at").asText(""));

        String apiCode = dataNode.path("code").asText(code);
        String currency = dataNode.path("currency").asText("USD");

        List<Map<String, Object>> history1W = buildFallbackHistory(latestPrice, 7, "day");
        List<Map<String, Object>> history1M = buildFallbackHistory(latestPrice, 4, "week");
        List<Map<String, Object>> history6M = buildFallbackHistory(latestPrice, 6, "month");

        BigDecimal high = maxValue(history1W);
        BigDecimal low = minValue(history1W);
        BigDecimal change = calcChange(history1W);
        BigDecimal changePercent = calcChangePercent(history1W);

        Map<String, Object> history = new LinkedHashMap<>();
        history.put("1W", history1W);
        history.put("1M", history1M);
        history.put("6M", history6M);

        Map<String, Object> item = new LinkedHashMap<>();
        item.put("symbol", buildDisplaySymbol(apiCode));
        item.put("name", buildName(apiCode, currency));
        item.put("date", latestTime);
        item.put("open", toBigDecimal(history1W.get(0).get("value")));
        item.put("high", high);
        item.put("low", low);
        item.put("close", latestPrice);
        item.put("change", change);
        item.put("changePercent", changePercent);
        item.put("history", history);

        return item;
    }

    private JsonNode queryOilApi(String code) {
        if (oilApiUrl == null || oilApiUrl.isBlank()) {
            throw new RuntimeException("app.oilprice.api.url is not configured");
        }
        if (oilApiToken == null || oilApiToken.isBlank()) {
            throw new RuntimeException("app.oilprice.api.token is not configured");
        }

        try {
            String requestUrl = oilApiUrl + "?by_code=" +
                    URLEncoder.encode(code, StandardCharsets.UTF_8);

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(requestUrl))
                    .timeout(Duration.ofSeconds(20))
                    .header(HttpHeaders.AUTHORIZATION, "Token " + oilApiToken)
                    .GET()
                    .build();

            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                throw new RuntimeException(
                        "Oil API request failed for " + code +
                                ", status=" + response.statusCode() +
                                ", body=" + response.body()
                );
            }

            return objectMapper.readTree(response.body());
        } catch (IOException e) {
            throw new RuntimeException("Failed to parse Oil API response for " + code + ": " + e.getMessage(), e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Oil API request interrupted for " + code + ": " + e.getMessage(), e);
        }
    }

    private String buildDisplaySymbol(String code) {
        if (WTI_CODE.equalsIgnoreCase(code)) {
            return "WTI";
        }
        if (BRENT_CODE.equalsIgnoreCase(code)) {
            return "BRENT";
        }
        return code;
    }

    private String buildName(String code, String currency) {
        if (WTI_CODE.equalsIgnoreCase(code)) {
            return "WTI原油";
        }
        if (BRENT_CODE.equalsIgnoreCase(code)) {
            return "Brent原油";
        }
        return code + " (" + currency + ")";
    }

    private String formatTime(String raw) {
        if (raw == null || raw.isBlank()) {
            return LocalDate.now().toString();
        }
        try {
            return OffsetDateTime.parse(raw).format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        } catch (Exception e) {
            return raw;
        }
    }

    private List<Map<String, Object>> buildFallbackHistory(BigDecimal latestPrice, int count, String unit) {
        List<Map<String, Object>> result = new ArrayList<>();
        BigDecimal step = new BigDecimal("0.08");

        for (int i = count - 1; i >= 0; i--) {
            BigDecimal value = latestPrice.subtract(step.multiply(BigDecimal.valueOf(i)))
                    .setScale(4, RoundingMode.HALF_UP);

            String label;
            if ("day".equals(unit)) {
                label = LocalDate.now().minusDays(i).toString();
            } else if ("week".equals(unit)) {
                label = "W" + (count - i);
            } else {
                label = "M" + (count - i);
            }

            Map<String, Object> point = new LinkedHashMap<>();
            point.put("date", label);
            point.put("value", value);
            result.add(point);
        }
        return result;
    }

    private BigDecimal maxValue(List<Map<String, Object>> points) {
        BigDecimal max = null;
        for (Map<String, Object> point : points) {
            BigDecimal value = toBigDecimal(point.get("value"));
            if (max == null || value.compareTo(max) > 0) {
                max = value;
            }
        }
        return max == null ? BigDecimal.ZERO.setScale(4, RoundingMode.HALF_UP)
                : max.setScale(4, RoundingMode.HALF_UP);
    }

    private BigDecimal minValue(List<Map<String, Object>> points) {
        BigDecimal min = null;
        for (Map<String, Object> point : points) {
            BigDecimal value = toBigDecimal(point.get("value"));
            if (min == null || value.compareTo(min) < 0) {
                min = value;
            }
        }
        return min == null ? BigDecimal.ZERO.setScale(4, RoundingMode.HALF_UP)
                : min.setScale(4, RoundingMode.HALF_UP);
    }

    private BigDecimal calcChange(List<Map<String, Object>> points) {
        if (points == null || points.size() < 2) {
            return BigDecimal.ZERO.setScale(4, RoundingMode.HALF_UP);
        }
        BigDecimal first = toBigDecimal(points.get(0).get("value"));
        BigDecimal last = toBigDecimal(points.get(points.size() - 1).get("value"));
        return last.subtract(first).setScale(4, RoundingMode.HALF_UP);
    }

    private BigDecimal calcChangePercent(List<Map<String, Object>> points) {
        if (points == null || points.size() < 2) {
            return BigDecimal.ZERO.setScale(4, RoundingMode.HALF_UP);
        }

        BigDecimal first = toBigDecimal(points.get(0).get("value"));
        BigDecimal change = calcChange(points);

        if (first.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ZERO.setScale(4, RoundingMode.HALF_UP);
        }

        return change.multiply(BigDecimal.valueOf(100))
                .divide(first, 4, RoundingMode.HALF_UP);
    }

    private BigDecimal toBigDecimal(Object value) {
        if (value == null) {
            return BigDecimal.ZERO.setScale(4, RoundingMode.HALF_UP);
        }
        return new BigDecimal(String.valueOf(value)).setScale(4, RoundingMode.HALF_UP);
    }
}