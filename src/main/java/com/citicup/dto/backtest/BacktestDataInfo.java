package com.citicup.dto.backtest;

import lombok.Builder;
import lombok.Data;

/** 本次回测所用数据的概览信息，方便前端展示数据可用性。 */
@Data
@Builder
public class BacktestDataInfo {
    /** 回测品种代码 */
    private String symbol;
    /** 实际用于回测的 OHLCV 总条数 */
    private int totalBars;
    /** 数据起始日期（YYYY-MM-DD） */
    private String dataStartDate;
    /** 数据结束日期（YYYY-MM-DD） */
    private String dataEndDate;
    /** 是否在 prediction_run 表中找到可用的 ML 预测数据 */
    private boolean mlPredictionsAvailable;
    /** 从 prediction_run 中提取到的预测日期数量 */
    private int mlPredictionCount;
    /** OHLCV 与 ML 预测的重叠交易日数量（AND/VETO/ModelOnly 的实际信号条数） */
    private int overlappingBars;
    /** 数据状态说明，包含缺失数据的提示和补充建议 */
    private String note;
}
