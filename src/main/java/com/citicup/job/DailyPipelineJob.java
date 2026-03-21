package com.citicup.job;

import com.citicup.service.OilPriceService;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.logging.Logger;

@Component
public class DailyPipelineJob {

    private static final Logger logger = Logger.getLogger(DailyPipelineJob.class.getName());

    private final OilPriceService oilPriceService;

    public DailyPipelineJob(OilPriceService oilPriceService) {
        this.oilPriceService = oilPriceService;
    }

    // 每天凌晨 1:00 执行（cron: second minute hour day month weekday）
    @Scheduled(cron = "0 0 1 * * ?")
    public void fetchOilPrice() {
        try {
            oilPriceService.fetchAndSaveOilPrice();
        } catch (Exception e) {
            logger.warning("DailyPipelineJob failed: " + e.getMessage());
        }
    }
}
