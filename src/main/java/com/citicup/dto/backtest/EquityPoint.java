package com.citicup.dto.backtest;

import lombok.AllArgsConstructor;
import lombok.Data;

/** 净值曲线上的一个数据点。 */
@Data
@AllArgsConstructor
public class EquityPoint {
    /** 交易日期，格式 YYYY-MM-DD */
    private String date;
    /** 当日累计净值，初始值为 1.0 */
    private double equity;
}
