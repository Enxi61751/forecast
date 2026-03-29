package com.citicup.dto.agent;

public class FactorSnapshotDto {

    private Double currentPrice;
    private double trendScore;
    private String rsiStatus;
    private String termStructure;
    private Double currentCalendarSpread;
    private Double historicalSpreadMean;
    private Double historicalSpreadStd;

    public Double getCurrentPrice() {
        return currentPrice;
    }

    public void setCurrentPrice(Double currentPrice) {
        this.currentPrice = currentPrice;
    }

    public double getTrendScore() {
        return trendScore;
    }

    public void setTrendScore(double trendScore) {
        this.trendScore = trendScore;
    }

    public String getRsiStatus() {
        return rsiStatus;
    }

    public void setRsiStatus(String rsiStatus) {
        this.rsiStatus = rsiStatus;
    }

    public String getTermStructure() {
        return termStructure;
    }

    public void setTermStructure(String termStructure) {
        this.termStructure = termStructure;
    }

    public Double getCurrentCalendarSpread() {
        return currentCalendarSpread;
    }

    public void setCurrentCalendarSpread(Double currentCalendarSpread) {
        this.currentCalendarSpread = currentCalendarSpread;
    }

    public Double getHistoricalSpreadMean() {
        return historicalSpreadMean;
    }

    public void setHistoricalSpreadMean(Double historicalSpreadMean) {
        this.historicalSpreadMean = historicalSpreadMean;
    }

    public Double getHistoricalSpreadStd() {
        return historicalSpreadStd;
    }

    public void setHistoricalSpreadStd(Double historicalSpreadStd) {
        this.historicalSpreadStd = historicalSpreadStd;
    }
}