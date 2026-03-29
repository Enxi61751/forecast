package com.citicup.dto.agent;
public class StandardOrderDto {

    private String orderId;
    private String parentOrderId;
    private String agentId;
    private String book;
    private String symbol;
    private String side;
    private String orderType;
    private int quantity;
    private int filledQuantity;
    private int remainingQuantity;
    private int ttlSteps;
    private String horizon;
    private String status;
    private double aggressiveness;
    private String priceStrategy;
    private String reason;

    public String getOrderId() {
        return orderId;
    }

    public void setOrderId(String orderId) {
        this.orderId = orderId;
    }

    public String getParentOrderId() {
        return parentOrderId;
    }

    public void setParentOrderId(String parentOrderId) {
        this.parentOrderId = parentOrderId;
    }

    public String getAgentId() {
        return agentId;
    }

    public void setAgentId(String agentId) {
        this.agentId = agentId;
    }

    public String getBook() {
        return book;
    }

    public void setBook(String book) {
        this.book = book;
    }

    public String getSymbol() {
        return symbol;
    }

    public void setSymbol(String symbol) {
        this.symbol = symbol;
    }

    public String getSide() {
        return side;
    }

    public void setSide(String side) {
        this.side = side;
    }

    public String getOrderType() {
        return orderType;
    }

    public void setOrderType(String orderType) {
        this.orderType = orderType;
    }

    public int getQuantity() {
        return quantity;
    }

    public void setQuantity(int quantity) {
        this.quantity = quantity;
    }

    public int getFilledQuantity() {
        return filledQuantity;
    }

    public void setFilledQuantity(int filledQuantity) {
        this.filledQuantity = filledQuantity;
    }

    public int getRemainingQuantity() {
        return remainingQuantity;
    }

    public void setRemainingQuantity(int remainingQuantity) {
        this.remainingQuantity = remainingQuantity;
    }

    public int getTtlSteps() {
        return ttlSteps;
    }

    public void setTtlSteps(int ttlSteps) {
        this.ttlSteps = ttlSteps;
    }

    public String getHorizon() {
        return horizon;
    }

    public void setHorizon(String horizon) {
        this.horizon = horizon;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public double getAggressiveness() {
        return aggressiveness;
    }

    public void setAggressiveness(double aggressiveness) {
        this.aggressiveness = aggressiveness;
    }

    public String getPriceStrategy() {
        return priceStrategy;
    }

    public void setPriceStrategy(String priceStrategy) {
        this.priceStrategy = priceStrategy;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }
}