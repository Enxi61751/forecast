package com.citicup.job;

import com.citicup.service.OilPriceService;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class DailyPipelineJob {

    private final OilPriceService oilPriceService;

    public DailyPipelineJob(OilPriceService oilPriceService) {
        this.oilPriceService = oilPriceService;
    }

    @Scheduled(cron = "0 0 * * * ?")
    public void fetchOilPrice() {

        oilPriceService.fetchAndSaveOilPrice();

    }
}
