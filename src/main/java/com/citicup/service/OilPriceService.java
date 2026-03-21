package com.citicup.service;

import com.citicup.dto.oilprice.OilPrice;
import com.citicup.dto.oilprice.OilPriceApiResponse;
import com.citicup.dto.oilprice.OilPriceData;
import com.citicup.entity.OilPriceHistory;
import com.citicup.repository.OilPriceHistoryRepo;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.logging.Logger;

@Service
public class OilPriceService {

    private static final Logger logger = Logger.getLogger(OilPriceService.class.getName());

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
        try {
            // 检查 token 是否为默认值
            if (apiToken == null || apiToken.equals("YOUR_OIL_API_TOKEN")) {
                logger.warning("Oil price API token not configured, returning mock data");
                return getMockOilPriceResponse();
            }

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
        } catch (HttpClientErrorException e) {
            logger.severe("Oil price API error: " + e.getStatusCode() + " - " + e.getResponseBodyAsString());
            return getMockOilPriceResponse();
        } catch (Exception e) {
            logger.severe("Oil price API call failed: " + e.getMessage());
            return getMockOilPriceResponse();
        }
    }

    private OilPriceApiResponse getMockOilPriceResponse() {
        // 返回模拟数据避免错误
        OilPriceApiResponse response = new OilPriceApiResponse();
        OilPriceData data = new OilPriceData();
        
        OilPrice wti = new OilPrice();
        wti.setPrice(75.50);
        wti.setCurrency("USD");
        wti.setUnit("barrel");
        wti.setChange("+0.5%");
        wti.setTimestamp(OffsetDateTime.now().toString());
        
        OilPrice brent = new OilPrice();
        brent.setPrice(80.25);
        brent.setCurrency("USD");
        brent.setUnit("barrel");
        brent.setChange("+0.3%");
        brent.setTimestamp(OffsetDateTime.now().toString());
        
        data.setWTI(wti);
        data.setBRENT(brent);
        response.setData(data);
        
        return response;
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
        entity.setTimestamp(OffsetDateTime.parse(priceData.getTimestamp()).toLocalDateTime());

        oilPriceHistoryRepo.save(entity);
    }
}
