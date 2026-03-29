package com.citicup.dto.agent;
public class MarketMicrostructureDto {

    private double bidAskSpread;
    private String orderBookDepth;
    private Double spreadBidAskSpread;
    private String spreadOrderBookDepth;
    private Double optionsBidAskSpread;
    private String optionsOrderBookDepth;

    public double getBidAskSpread() {
        return bidAskSpread;
    }

    public void setBidAskSpread(double bidAskSpread) {
        this.bidAskSpread = bidAskSpread;
    }

    public String getOrderBookDepth() {
        return orderBookDepth;
    }

    public void setOrderBookDepth(String orderBookDepth) {
        this.orderBookDepth = orderBookDepth;
    }

    public Double getSpreadBidAskSpread() {
        return spreadBidAskSpread;
    }

    public void setSpreadBidAskSpread(Double spreadBidAskSpread) {
        this.spreadBidAskSpread = spreadBidAskSpread;
    }

    public String getSpreadOrderBookDepth() {
        return spreadOrderBookDepth;
    }

    public void setSpreadOrderBookDepth(String spreadOrderBookDepth) {
        this.spreadOrderBookDepth = spreadOrderBookDepth;
    }

    public Double getOptionsBidAskSpread() {
        return optionsBidAskSpread;
    }

    public void setOptionsBidAskSpread(Double optionsBidAskSpread) {
        this.optionsBidAskSpread = optionsBidAskSpread;
    }

    public String getOptionsOrderBookDepth() {
        return optionsOrderBookDepth;
    }

    public void setOptionsOrderBookDepth(String optionsOrderBookDepth) {
        this.optionsOrderBookDepth = optionsOrderBookDepth;
    }
}