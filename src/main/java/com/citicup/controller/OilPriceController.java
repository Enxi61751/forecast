package com.citicup.controller;

import com.citicup.dto.oilprice.OilPriceApiResponse;
import com.citicup.entity.OilPriceHistory;
import com.citicup.service.OilPriceService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/oilprice")
public class OilPriceController {

    private final OilPriceService oilPriceService;

    public OilPriceController(OilPriceService oilPriceService) {
        this.oilPriceService = oilPriceService;
    }

    @GetMapping("/latest")
    public OilPriceApiResponse getLatestOilPrice() {
        return oilPriceService.getLatestOilPrice();
    }

    @GetMapping("/history")
    public List<OilPriceHistory> getHistory(
        @RequestParam String start,
        @RequestParam String end) {

    return oilPriceService.getHistoryPrices(start, end);
}

}
