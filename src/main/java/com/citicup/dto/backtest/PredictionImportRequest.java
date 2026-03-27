package com.citicup.dto.backtest;

import lombok.Data;
import java.util.List;

/**
 * 批量导入历史预测数据的请求体。
 *
 * <p>示例：
 * <pre>
 * {
 *   "target": "WTI",
 *   "horizon": "1d",
 *   "predictions": [
 *     {"date": "2022-01-04", "value": 75.3},
 *     {"date": "2022-01-05", "value": 74.8}
 *   ]
 * }
 * </pre>
 *
 * <p>{@code date} 是预测的目标日期（即"预测哪天的收盘价"），{@code value} 是预测价格。
 */
@Data
public class PredictionImportRequest {

    /** 预测标的，与 prediction_run.target 一致，如 WTI 或 Brent */
    private String target = "WTI";

    /** 预测周期，通常用 "1d"（回测目前只使用 1d） */
    private String horizon = "1d";

    /** 预测数据列表，每条包含目标日期和预测价格 */
    private List<PredictionEntry> predictions;

    @Data
    public static class PredictionEntry {
        /** 预测目标日期，格式 YYYY-MM-DD */
        private String date;
        /** 预测收盘价（美元/桶） */
        private double value;
    }
}
