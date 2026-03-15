package com.citicup.controller;

import com.citicup.dto.oilprice.OilPrice;
import com.citicup.dto.oilprice.OilPriceApiResponse;
import com.citicup.dto.oilprice.OilPriceData;
import com.citicup.entity.OilPriceHistory;
import com.citicup.service.OilPriceService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(OilPriceController.class)
class OilPriceControllerTest {

    @Autowired MockMvc mvc;
    @MockBean OilPriceService oilPriceService;

    @Test
    void getHistory_wrapsInApiResponse() throws Exception {
        OilPriceHistory h = OilPriceHistory.builder()
                .id(1L).type("WTI").price(70.5)
                .currency("USD").unit("per barrel")
                .timestamp(LocalDateTime.of(2025, 1, 15, 0, 0))
                .build();

        when(oilPriceService.getHistoryPrices(any(), any())).thenReturn(List.of(h));

        mvc.perform(get("/api/oilprice/history")
                        .param("start", "2025-01-01T00:00:00")
                        .param("end", "2025-01-31T00:00:00"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data[0].type").value("WTI"))
                .andExpect(jsonPath("$.data[0].price").value(70.5));
    }

    @Test
    void getLatestOilPrice_wrapsInApiResponse() throws Exception {
        OilPrice wti = new OilPrice();
        wti.setPrice(72.0);
        wti.setCurrency("USD");
        wti.setUnit("per barrel");
        wti.setTimestamp("2025-01-15T00:00:00Z");

        OilPriceData data = new OilPriceData();
        data.setWTI(wti);

        OilPriceApiResponse apiResponse = new OilPriceApiResponse();
        apiResponse.setStatus("success");
        apiResponse.setData(data);

        when(oilPriceService.getLatestOilPrice()).thenReturn(apiResponse);

        mvc.perform(get("/api/oilprice/latest"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(0))
                .andExpect(jsonPath("$.data.status").value("success"))
                .andExpect(jsonPath("$.data.data.wti.price").value(72.0));
    }
}
