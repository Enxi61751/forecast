package com.citicup.service;

import com.citicup.service.client.Stage2AgentClient;
import com.fasterxml.jackson.databind.JsonNode;
import com.citicup.dto.agent.*;
import org.springframework.stereotype.Service;

@Service
public class AgentService {

    private final Stage2AgentClient stage2AgentClient;

    public AgentService(Stage2AgentClient stage2AgentClient) {
        this.stage2AgentClient = stage2AgentClient;
    }

    public JsonNode simulateSingleDemo() {
        Stage2SingleRequest request = buildDemoRequest();
        return stage2AgentClient.simulateSingle(request);
    }

    private Stage2SingleRequest buildDemoRequest() {
        FactorSnapshotDto factorSnapshot = new FactorSnapshotDto();
        factorSnapshot.setCurrentPrice(78.5);
        factorSnapshot.setTrendScore(0.72);
        factorSnapshot.setRsiStatus("Overbought");
        factorSnapshot.setTermStructure("Backwardation");
        factorSnapshot.setCurrentCalendarSpread(1.2);
        factorSnapshot.setHistoricalSpreadMean(0.6);
        factorSnapshot.setHistoricalSpreadStd(0.3);

        TailRiskReportDto tailRiskReport = new TailRiskReportDto();
        tailRiskReport.setGammaProfile("Short Gamma");
        tailRiskReport.setLiquidityStress(0.65);

        MarketMicrostructureDto micro = new MarketMicrostructureDto();
        micro.setBidAskSpread(0.08);
        micro.setOrderBookDepth("Thin");
        micro.setSpreadBidAskSpread(0.05);
        micro.setSpreadOrderBookDepth("Normal");
        micro.setOptionsBidAskSpread(0.12);
        micro.setOptionsOrderBookDepth("Thin");

        SessionInfoDto sessionInfo = new SessionInfoDto();
        sessionInfo.setPhase("Mid-Day");
        sessionInfo.setTimeToClose(120);

        EnvironmentDto environment = new EnvironmentDto();
        environment.setFactorSnapshot(factorSnapshot);
        environment.setTailRiskReport(tailRiskReport);
        environment.setMarketMicrostructure(micro);
        environment.setSessionInfo(sessionInfo);

        EventDto event = new EventDto();
        event.setHeadline("OPEC hints at deeper supply cuts");
        event.setBody("Market reacts to renewed supply concerns...");
        event.setSource("Reuters");
        event.setImpactType("Supply");
        event.setSentimentScore(1.8);

        SelfStateDto self = new SelfStateDto();
        self.setRole("speculator");
        self.setMandate("short-term directional trading");
        self.setHedgerType("neutral");
        self.setMaxLeverage(3.0);
        self.setStopLossPct(0.03);
        self.setPosition(10);
        self.setUnrealizedPnl(2500);
        self.setUnrealizedPnlPct(0.04);
        self.setCashLevel(100000);
        self.setLastAction("BUY");
        self.setConsecutiveLosses(0);
        self.setViewHistory("Bullish on supply shock");

        SimulationInputDto input = new SimulationInputDto();
        input.setEnvironment(environment);
        input.setEvent(event);
        input.setSelfState(self);

        Stage2SingleRequest request = new Stage2SingleRequest();
        request.setSimulationInput(input);
        request.setCurrentPrice(78.5);
        request.setCurrentVolatility(0.24);
        request.setDealerInventory(-120);
        request.setMaxPositionLimit(500);
        request.setSeed(7);

        return request;
    }
}