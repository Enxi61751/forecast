package com.citicup.dto.oilprice;


public class OilPriceApiResponse {

    private String status;
    private OilPriceData data;

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public OilPriceData getData() {
        return data;
    }

    public void setData(OilPriceData data) {
        this.data = data;
    }
}
