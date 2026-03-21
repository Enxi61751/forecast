package com.citicup.config;

import com.citicup.entity.*;
import com.citicup.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final NewsRepository newsRepository;
    private final ExchangeRepository exchangeRepository;
    private final OilPriceHistoryRepo oilPriceHistoryRepo;
    private final PredictionRunRepo predictionRunRepo;
    private final RiskReportRepo riskReportRepo;
    private final EventRepository eventRepository;

    @Override
    public void run(String... args) throws Exception {
        System.out.println("========= DataInitializer started =========");
        try {
            long newsCount = newsRepository.count();
            long eventCount = eventRepository.count();
            System.out.println("Current news count: " + newsCount + ", event count: " + eventCount);
            
            if (newsCount == 0) {
                System.out.println("Starting data initialization...");
                initializeNews();
                System.out.println("✅ News initialized: " + newsRepository.count() + " records");
                
                initializeExchange();
                System.out.println("✅ Exchange initialized: " + exchangeRepository.count() + " records");
                
                initializeOilPrices();
                System.out.println("✅ Oil prices initialized: " + oilPriceHistoryRepo.count() + " records");
                
                initializePredictions();
                System.out.println("✅ Predictions initialized");
            } else {
                System.out.println("ℹ️ Database already contains " + newsCount + " news records, skipping base initialization");
            }
            
            // Always check and initialize events
            if (eventCount == 0) {
                initializeEvents();
                System.out.println("✅ Events initialized: " + eventRepository.count() + " records");
            } else {
                System.out.println("ℹ️ Events already exist (" + eventCount + " records)");
            }
            
            System.out.println("✅✅ Data initialization check completed!");
        } catch (Exception e) {
            System.out.println("❌ Error during data initialization: " + e.getMessage());
            e.printStackTrace();
        }
        System.out.println("========= DataInitializer finished =========");
    }

    private void initializeNews() {
        newsRepository.save(News.builder()
                .title("全球油价持续上升")
                .source("Reuters")
                .summary("受OPEC+减产影响，WTI原油价格跟随上升走势")
                .url("https://example.com/news1")
                .publishedAt(LocalDateTime.now().minusDays(1))
                .sentimentLabel("positive")
                .sentimentScore(0.75)
                .build());

        newsRepository.save(News.builder()
                .title("美元指数承压")
                .source("Bloomberg")
                .summary("美联储政策转向鸽派，美元开始回落")
                .url("https://example.com/news2")
                .publishedAt(LocalDateTime.now().minusHours(12))
                .sentimentLabel("neutral")
                .sentimentScore(0.62)
                .build());

        newsRepository.save(News.builder()
                .title("中东局势升温")
                .source("CNBC")
                .summary("地缘政治风险推动能源价格上涨")
                .url("https://example.com/news3")
                .publishedAt(LocalDateTime.now().minusHours(6))
                .sentimentLabel("negative")
                .sentimentScore(0.45)
                .build());
    }

    private void initializeExchange() {
        for (int i = 5; i >= 0; i--) {
            Exchange ex = Exchange.builder()
                    .date(LocalDate.now().minusDays(i))
                    .rate(7.18 + i * 0.01)
                    .build();
            exchangeRepository.save(ex);
        }
    }

    private void initializeOilPrices() {
        double[] wtiPrices = {76.50, 75.80, 77.20, 78.10, 77.50, 78.90, 79.50, 80.25};
        double[] brentPrices = {81.10, 80.40, 81.80, 82.70, 81.90, 83.30, 83.95, 84.70};

        for (int i = 0; i < wtiPrices.length; i++) {
            OilPriceHistory wti = OilPriceHistory.builder()
                    .type("WTI")
                    .price(wtiPrices[i])
                    .currency("USD")
                    .unit("barrel")
                    .changePercent(i % 2 == 0 ? "+1.2%" : "-0.9%")
                    .timestamp(LocalDateTime.now().minusDays(7 - i))
                    .build();
            oilPriceHistoryRepo.save(wti);

            OilPriceHistory brent = OilPriceHistory.builder()
                    .type("BRENT")
                    .price(brentPrices[i])
                    .currency("USD")
                    .unit("barrel")
                    .changePercent(i % 2 == 0 ? "+1.1%" : "-0.9%")
                    .timestamp(LocalDateTime.now().minusDays(7 - i))
                    .build();
            oilPriceHistoryRepo.save(brent);
        }
    }

    private void initializePredictions() {
        PredictionRun pred1 = predictionRunRepo.save(PredictionRun.builder()
                .target("WTI")
                .horizon("7d")
                .runAt(Instant.now().minusSeconds(2 * 86400))
                .forecastJson("{\"predictions\":[{\"date\":\"2026-03-28\",\"value\":81.2},{\"date\":\"2026-03-29\",\"value\":81.8}]}")
                .extremeClsJson("{\"class\":\"normal\",\"confidence\":0.92}")
                .build());

        predictionRunRepo.save(PredictionRun.builder()
                .target("WTI")
                .horizon("30d")
                .runAt(Instant.now().minusSeconds(86400))
                .forecastJson("{\"predictions\":[{\"date\":\"2026-04-15\",\"value\":79.5}]}")
                .extremeClsJson("{\"class\":\"normal\",\"confidence\":0.88}")
                .build());

        predictionRunRepo.save(PredictionRun.builder()
                .target("BRENT")
                .horizon("7d")
                .runAt(Instant.now())
                .forecastJson("{\"predictions\":[{\"date\":\"2026-03-28\",\"value\":85.6}]}")
                .extremeClsJson("{\"class\":\"normal\",\"confidence\":0.90}")
                .build());

        // Initialize reports for first prediction
        riskReportRepo.save(RiskReport.builder()
                .predictionRunId(pred1.getId())
                .createdAt(Instant.now().minusSeconds(86400))
                .reportText("油价风险快报：预测WTI油价在未来7天内保持上升趋势")
                .materialsJson("{\"agents\":[{\"name\":\"fundamental\"}]}")
                .build());
    }

    private void initializeEvents() {
        eventRepository.save(Event.builder()
                .title("OPEC+ 紧急会议")
                .eventType("policy_decision")
                .summary("OPEC+ 宣布延续减产政策至年底")
                .intensity(0.85)
                .occurredAt(LocalDateTime.now().minusDays(3))
                .build());

        eventRepository.save(Event.builder()
                .title("美国库存数据公布")
                .eventType("data_release")
                .summary("美国原油库存意外大幅下降")
                .intensity(0.72)
                .occurredAt(LocalDateTime.now().minusDays(1))
                .build());

        eventRepository.save(Event.builder()
                .title("中东地缘政治紧张")
                .eventType("geopolitical")
                .summary("中东局势升温，引发能源价格上涨预期")
                .intensity(0.78)
                .occurredAt(LocalDateTime.now())
                .build());
    }
}
