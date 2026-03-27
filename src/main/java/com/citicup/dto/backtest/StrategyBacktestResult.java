package com.citicup.dto.backtest;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;
import java.util.List;

/** 单个策略的完整回测结果。 */
@Data
@Builder
public class StrategyBacktestResult {
    /** 策略名称，如 "Aberration(baseOnly)"、"MACD+Model(AND)" */
    private String strategyName;

    // ---------- 基础交易统计 ----------
    /** 总交易次数（有持仓信号的交易日数） */
    @JsonProperty("nTrades")
    private int nTrades;
    /** 胜率（盈利交易日 / 总交易日） */
    private double winRate;
    /** 全样本期末总收益率（小数，如 0.23 表示 +23%） */
    private double totalReturn;
    /** 全样本最大回撤（负数小数） */
    private double maxDrawdown;
    /** 每笔交易平均收益率 */
    private double avgReturnPerTrade;
    /** 盈利交易的平均收益率 */
    private double avgWin;
    /** 亏损交易的平均收益率（负数） */
    private double avgLoss;
    /** 盈亏比（总盈利 / 总亏损绝对值）；无亏损时为 999 */
    private double profitFactor;

    // ---------- 样本外（最后 20%）指标 ----------
    /** 样本外总收益率 */
    private double oosReturn;
    /** 样本外胜率 */
    private double oosWinRate;
    /** 样本外最大回撤（负数） */
    private double oosMaxDrawdown;
    /** 全样本内 63 日滚动窗口的最差最大回撤（负数） */
    private double worstRollingDrawdown63d;

    // ---------- 时序数据 ----------
    /** 日度净值曲线，每条 {date, equity}，equity 初始为 1.0 */
    private List<EquityPoint> equityCurve;
    /** 成本敏感性分析：费率倍数 x1/x2/x3 下的扣费后指标 */
    private List<CostSensitivityPoint> costSensitivity;
}
