package com.citicup.service;

import com.citicup.entity.OilPriceHistory;
import com.citicup.repository.OilPriceHistoryRepo;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OilPriceServiceTest {

    @Mock RestTemplate restTemplate;
    @Mock OilPriceHistoryRepo oilPriceHistoryRepo;
    @InjectMocks OilPriceService oilPriceService;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(oilPriceService, "apiUrl", "https://api.example.com/oilprice");
        ReflectionTestUtils.setField(oilPriceService, "apiToken", "test-token");
    }

    @Test
    void getHistoryPrices_returnsFromRepo() {
        String start = "2025-01-01T00:00:00";
        String end = "2025-01-31T00:00:00";
        LocalDateTime startDt = LocalDateTime.parse(start);
        LocalDateTime endDt = LocalDateTime.parse(end);

        OilPriceHistory h = OilPriceHistory.builder()
                .id(1L).type("WTI").price(70.0)
                .currency("USD").unit("per barrel")
                .timestamp(startDt)
                .build();
        when(oilPriceHistoryRepo.findByTimestampBetween(startDt, endDt)).thenReturn(List.of(h));

        List<OilPriceHistory> result = oilPriceService.getHistoryPrices(start, end);

        assertEquals(1, result.size());
        assertEquals("WTI", result.get(0).getType());
        assertEquals(70.0, result.get(0).getPrice());
    }

    @Test
    void getHistoryPrices_emptyRange_returnsEmpty() {
        String start = "2025-06-01T00:00:00";
        String end = "2025-06-30T00:00:00";
        LocalDateTime startDt = LocalDateTime.parse(start);
        LocalDateTime endDt = LocalDateTime.parse(end);

        when(oilPriceHistoryRepo.findByTimestampBetween(startDt, endDt)).thenReturn(List.of());

        List<OilPriceHistory> result = oilPriceService.getHistoryPrices(start, end);

        assertTrue(result.isEmpty());
    }
}
