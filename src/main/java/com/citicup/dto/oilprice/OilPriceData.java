package com.citicup.dto.oilprice;


public class OilPriceData {

    private OilPrice WTI;
    private OilPrice BRENT;

    public OilPrice getWTI() {
        return WTI;
    }

    public void setWTI(OilPrice WTI) {
        this.WTI = WTI;
    }

    public OilPrice getBRENT() {
        return BRENT;
    }

    public void setBRENT(OilPrice BRENT) {
        this.BRENT = BRENT;
    }
}
