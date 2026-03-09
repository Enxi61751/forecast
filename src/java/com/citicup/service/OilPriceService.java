package com.citicup.service;

import com.citicup.dto.oilprice.OilPriceApiResponse;
import com.citicup.entity.OilPriceHistory;
import com.citicup.respository.OilPriceHistoryRepo;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class OilPriceService {

    private final RestTemplate restTemplate;
    private final OilPriceHistoryRepo oilPriceHistoryRepo;

    @Value("${app.oilprice.api.url}")
    private String apiUrl;

    @Value("${app.oilprice.api.token}")
    private String apiToken;

    public OilPriceService(RestTemplate restTemplate,
                           OilPriceHistoryRepo oilPriceHistoryRepo) {
        this.restTemplate = restTemplate;
        this.oilPriceHistoryRepo = oilPriceHistoryRepo;
    }

    public OilPriceApiResponse getLatestOilPrice() {

        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Token " + apiToken);
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<String> entity = new HttpEntity<>(headers);

        ResponseEntity<OilPriceApiResponse> response =
                restTemplate.exchange(
                        apiUrl,
                        HttpMethod.GET,
                        entity,
                        OilPriceApiResponse.class
                );

        return response.getBody();
    }

    public List<OilPriceHistory> getHistoryPrices(String start, String end) {

        LocalDateTime startTime = LocalDateTime.parse(start);
        LocalDateTime endTime = LocalDateTime.parse(end);

        return oilPriceHistoryRepo.findByTimestampBetween(startTime, endTime);
    }

    public void fetchAndSaveOilPrice() {

        OilPriceApiResponse response = getLatestOilPrice();

        OilPriceData data = response.getData();

        saveOilPrice("WTI", data.getWTI());
        saveOilPrice("BRENT", data.getBRENT());

    }

    private void saveOilPrice(String type, OilPrice priceData) {

        OilPriceHistory entity = new OilPriceHistory();

        entity.setType(type);
        entity.setPrice(priceData.getPrice());
        entity.setCurrency(priceData.getCurrency());
        entity.setUnit(priceData.getUnit());
        entity.setChangePercent(priceData.getChange());
        entity.setTimestamp(LocalDateTime.parse(priceData.getTimestamp()));

        oilPriceHistoryRepo.save(entity);
    }
}
