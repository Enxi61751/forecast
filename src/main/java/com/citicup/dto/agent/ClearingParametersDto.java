package com.citicup.dto.agent;
public class ClearingParametersDto {

    private double lambdaBase;
    private double alphaRecovery;
    private double betaConsumption;
    private double noiseScale;
    private double volatilitySensitivity;
    private int shortGammaInventoryThreshold;
    private int longGammaInventoryThreshold;
    private double shortGammaVolMultiplier;
    private double spreadWideningMultiplier;
    private double temporaryImpactMultiplier;

    public double getLambdaBase() {
        return lambdaBase;
    }

    public void setLambdaBase(double lambdaBase) {
        this.lambdaBase = lambdaBase;
    }

    public double getAlphaRecovery() {
        return alphaRecovery;
    }

    public void setAlphaRecovery(double alphaRecovery) {
        this.alphaRecovery = alphaRecovery;
    }

    public double getBetaConsumption() {
        return betaConsumption;
    }

    public void setBetaConsumption(double betaConsumption) {
        this.betaConsumption = betaConsumption;
    }

    public double getNoiseScale() {
        return noiseScale;
    }

    public void setNoiseScale(double noiseScale) {
        this.noiseScale = noiseScale;
    }

    public double getVolatilitySensitivity() {
        return volatilitySensitivity;
    }

    public void setVolatilitySensitivity(double volatilitySensitivity) {
        this.volatilitySensitivity = volatilitySensitivity;
    }

    public int getShortGammaInventoryThreshold() {
        return shortGammaInventoryThreshold;
    }

    public void setShortGammaInventoryThreshold(int shortGammaInventoryThreshold) {
        this.shortGammaInventoryThreshold = shortGammaInventoryThreshold;
    }

    public int getLongGammaInventoryThreshold() {
        return longGammaInventoryThreshold;
    }

    public void setLongGammaInventoryThreshold(int longGammaInventoryThreshold) {
        this.longGammaInventoryThreshold = longGammaInventoryThreshold;
    }

    public double getShortGammaVolMultiplier() {
        return shortGammaVolMultiplier;
    }

    public void setShortGammaVolMultiplier(double shortGammaVolMultiplier) {
        this.shortGammaVolMultiplier = shortGammaVolMultiplier;
    }

    public double getSpreadWideningMultiplier() {
        return spreadWideningMultiplier;
    }

    public void setSpreadWideningMultiplier(double spreadWideningMultiplier) {
        this.spreadWideningMultiplier = spreadWideningMultiplier;
    }

    public double getTemporaryImpactMultiplier() {
        return temporaryImpactMultiplier;
    }

    public void setTemporaryImpactMultiplier(double temporaryImpactMultiplier) {
        this.temporaryImpactMultiplier = temporaryImpactMultiplier;
    }
}