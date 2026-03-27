package com.citicup.dto.backtest;

import lombok.AllArgsConstructor;
import lombok.Data;

/** 成本敏感性分析中的一行：在不同费率倍数下的净收益和最大回撤。 */
@Data
@AllArgsConstructor
public class CostSensitivityPoint {
    /** 费率倍数（1.0 = 基础费率，2.0 = 两倍，3.0 = 三倍） */
    private double costMultiplier;
    /** 扣费后总收益率（小数） */
    private double netTotalReturn;
    /** 扣费后最大回撤（负数小数） */
    private double netMaxDrawdown;
}
