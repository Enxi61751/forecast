package com.citicup.dto.oil;

import com.citicup.dto.oil.OilPrice;

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
