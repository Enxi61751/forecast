package com.citicup.dto.backtest;

import lombok.Data;
import java.time.LocalDate;
import java.util.List;

@Data
public class BacktestRequest {
    /**
     * 品种代码，与数据库 oil_price_daily_ohlcv.symbol 保持一致，例如 LCO1。
     * 可通过 GET /api/backtest/symbols 查询库中可用品种。
     */
    private String symbol = "LCO1";

    /** 回测起始日期（含），不填则使用数据库中该品种的最早日期。 */
    private LocalDate startDate;

    /** 回测结束日期（含），不填则使用数据库中该品种的最新日期。 */
    private LocalDate endDate;

    /**
     * 要运行的基础策略列表（不区分大小写）。
     * 可选值：Aberration、DualThrust、MACD、Momentum、ModelOnly
     * 不填或空列表时运行全部策略。
     */
    private List<String> strategies;

    /**
     * 组合模式列表（不区分大小写）。
     * 可选值：baseOnly、AND、VETO
     * 不填或空列表时运行全部模式。
     */
    private List<String> combineModes;

    /**
     * 单边费率（手续费 + 滑点），单位为小数（如 0.0005 表示 5bps）。
     * 默认 0.0005；仅用于成本敏感性分析，不影响基础回测指标。
     */
    private double feeSlipRatePerSide = 0.0005;
}
