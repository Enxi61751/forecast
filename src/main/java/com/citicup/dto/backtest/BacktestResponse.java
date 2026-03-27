package com.citicup.dto.backtest;

import lombok.Builder;
import lombok.Data;
import java.util.List;

@Data
@Builder
public class BacktestResponse {
    /** 本次回测使用的数据信息 */
    private BacktestDataInfo dataInfo;
    /** 每个策略/组合模式的独立回测结果列表 */
    private List<StrategyBacktestResult> results;
}
