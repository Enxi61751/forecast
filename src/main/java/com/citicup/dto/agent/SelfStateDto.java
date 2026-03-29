package com.citicup.dto.agent;
public class SelfStateDto {

    private String role;
    private String mandate;
    private String hedgerType = "neutral";
    private double maxLeverage;
    private double stopLossPct;
    private double position;
    private double unrealizedPnl;
    private double unrealizedPnlPct;
    private double cashLevel;
    private String lastAction;
    private int consecutiveLosses;
    private String viewHistory;

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public String getMandate() {
        return mandate;
    }

    public void setMandate(String mandate) {
        this.mandate = mandate;
    }

    public String getHedgerType() {
        return hedgerType;
    }

    public void setHedgerType(String hedgerType) {
        this.hedgerType = hedgerType;
    }

    public double getMaxLeverage() {
        return maxLeverage;
    }

    public void setMaxLeverage(double maxLeverage) {
        this.maxLeverage = maxLeverage;
    }

    public double getStopLossPct() {
        return stopLossPct;
    }

    public void setStopLossPct(double stopLossPct) {
        this.stopLossPct = stopLossPct;
    }

    public double getPosition() {
        return position;
    }

    public void setPosition(double position) {
        this.position = position;
    }

    public double getUnrealizedPnl() {
        return unrealizedPnl;
    }

    public void setUnrealizedPnl(double unrealizedPnl) {
        this.unrealizedPnl = unrealizedPnl;
    }

    public double getUnrealizedPnlPct() {
        return unrealizedPnlPct;
    }

    public void setUnrealizedPnlPct(double unrealizedPnlPct) {
        this.unrealizedPnlPct = unrealizedPnlPct;
    }

    public double getCashLevel() {
        return cashLevel;
    }

    public void setCashLevel(double cashLevel) {
        this.cashLevel = cashLevel;
    }

    public String getLastAction() {
        return lastAction;
    }

    public void setLastAction(String lastAction) {
        this.lastAction = lastAction;
    }

    public int getConsecutiveLosses() {
        return consecutiveLosses;
    }

    public void setConsecutiveLosses(int consecutiveLosses) {
        this.consecutiveLosses = consecutiveLosses;
    }

    public String getViewHistory() {
        return viewHistory;
    }

    public void setViewHistory(String viewHistory) {
        this.viewHistory = viewHistory;
    }
}