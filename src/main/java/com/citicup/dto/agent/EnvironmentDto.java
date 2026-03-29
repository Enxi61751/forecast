package com.citicup.dto.agent;

public class EnvironmentDto {

    private FactorSnapshotDto factorSnapshot;
    private TailRiskReportDto tailRiskReport;
    private MarketMicrostructureDto marketMicrostructure;
    private SessionInfoDto sessionInfo;

    public FactorSnapshotDto getFactorSnapshot() {
        return factorSnapshot;
    }

    public void setFactorSnapshot(FactorSnapshotDto factorSnapshot) {
        this.factorSnapshot = factorSnapshot;
    }

    public TailRiskReportDto getTailRiskReport() {
        return tailRiskReport;
    }

    public void setTailRiskReport(TailRiskReportDto tailRiskReport) {
        this.tailRiskReport = tailRiskReport;
    }

    public MarketMicrostructureDto getMarketMicrostructure() {
        return marketMicrostructure;
    }

    public void setMarketMicrostructure(MarketMicrostructureDto marketMicrostructure) {
        this.marketMicrostructure = marketMicrostructure;
    }

    public SessionInfoDto getSessionInfo() {
        return sessionInfo;
    }

    public void setSessionInfo(SessionInfoDto sessionInfo) {
        this.sessionInfo = sessionInfo;
    }
}