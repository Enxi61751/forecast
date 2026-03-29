package com.citicup.dto.agent;
public class ClearingCalibrationObservationDto {

    private double effectiveNetFlow;
    private double liquidityStress;
    private double currentBidAskSpread;
    private double urgencyPressure;
    private double currentPrice;
    private double priceChange;
    private double totalVolume;
    private double nextLiquidityStress;
    private double currentVolatility;
    private double nextVolatility;
    private String nextGammaProfile;
    private double updatedBidAskSpread;

    public double getEffectiveNetFlow() {
        return effectiveNetFlow;
    }

    public void setEffectiveNetFlow(double effectiveNetFlow) {
        this.effectiveNetFlow = effectiveNetFlow;
    }

    public double getLiquidityStress() {
        return liquidityStress;
    }

    public void setLiquidityStress(double liquidityStress) {
        this.liquidityStress = liquidityStress;
    }

    public double getCurrentBidAskSpread() {
        return currentBidAskSpread;
    }

    public void setCurrentBidAskSpread(double currentBidAskSpread) {
        this.currentBidAskSpread = currentBidAskSpread;
    }

    public double getUrgencyPressure() {
        return urgencyPressure;
    }

    public void setUrgencyPressure(double urgencyPressure) {
        this.urgencyPressure = urgencyPressure;
    }

    public double getCurrentPrice() {
        return currentPrice;
    }

    public void setCurrentPrice(double currentPrice) {
        this.currentPrice = currentPrice;
    }

    public double getPriceChange() {
        return priceChange;
    }

    public void setPriceChange(double priceChange) {
        this.priceChange = priceChange;
    }

    public double getTotalVolume() {
        return totalVolume;
    }

    public void setTotalVolume(double totalVolume) {
        this.totalVolume = totalVolume;
    }

    public double getNextLiquidityStress() {
        return nextLiquidityStress;
    }

    public void setNextLiquidityStress(double nextLiquidityStress) {
        this.nextLiquidityStress = nextLiquidityStress;
    }

    public double getCurrentVolatility() {
        return currentVolatility;
    }

    public void setCurrentVolatility(double currentVolatility) {
        this.currentVolatility = currentVolatility;
    }

    public double getNextVolatility() {
        return nextVolatility;
    }

    public void setNextVolatility(double nextVolatility) {
        this.nextVolatility = nextVolatility;
    }

    public String getNextGammaProfile() {
        return nextGammaProfile;
    }

    public void setNextGammaProfile(String nextGammaProfile) {
        this.nextGammaProfile = nextGammaProfile;
    }

    public double getUpdatedBidAskSpread() {
        return updatedBidAskSpread;
    }

    public void setUpdatedBidAskSpread(double updatedBidAskSpread) {
        this.updatedBidAskSpread = updatedBidAskSpread;
    }
}