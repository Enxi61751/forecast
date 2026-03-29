package com.citicup.dto.agent;
public class TailRiskReportDto {

    private String gammaProfile;
    private double liquidityStress;

    public String getGammaProfile() {
        return gammaProfile;
    }

    public void setGammaProfile(String gammaProfile) {
        this.gammaProfile = gammaProfile;
    }

    public double getLiquidityStress() {
        return liquidityStress;
    }

    public void setLiquidityStress(double liquidityStress) {
        this.liquidityStress = liquidityStress;
    }
}