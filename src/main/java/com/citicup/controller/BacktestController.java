package com.citicup.controller;

import com.citicup.common.ApiResponse;
import com.citicup.dto.backtest.BacktestRequest;
import com.citicup.dto.backtest.BacktestResponse;
import com.citicup.dto.backtest.PredictionImportRequest;
import com.citicup.service.BacktestService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 策略回测 API。
 *
 * <pre>
 * GET  /api/backtest           - 使用说明及可用品种
 * GET  /api/backtest/symbols   - 数据库中可用品种及日期范围
 * POST /api/backtest/run       - 执行回测（主接口）
 * </pre>
 */
@RestController
@RequestMapping("/api/backtest")
@RequiredArgsConstructor
public class BacktestController {

    private final BacktestService backtestService;

    /**
     * GET /api/backtest — 简要使用说明，方便浏览器直接访问时快速了解接口。
     */
    @GetMapping
    public ApiResponse<Map<String, Object>> usage() {
        Map<String, Object> hint = new LinkedHashMap<>();
        hint.put("description", "策略回测接口：使用历史 OHLCV 数据模拟 Aberration / DualThrust / MACD / Momentum 等策略的历史表现");
        hint.put("endpoints", new String[]{
                "GET  /api/backtest/symbols              查看可用品种及日期范围",
                "POST /api/backtest/run                  执行回测（参见 exampleRequest）",
                "POST /api/backtest/import-predictions   批量导入历史预测（启用 AND/VETO/ModelOnly 策略）"
        });
        hint.put("exampleRequest", Map.of(
                "symbol", "LCO1",
                "startDate", "2022-01-01",
                "endDate", "2024-12-31",
                "strategies", new String[]{"Aberration", "DualThrust", "MACD", "Momentum", "ModelOnly"},
                "combineModes", new String[]{"baseOnly", "AND", "VETO"},
                "feeSlipRatePerSide", 0.0005
        ));
        hint.put("note", "strategies 和 combineModes 不填时默认运行全部；" +
                         "AND/VETO/ModelOnly 需要先通过 POST /api/predict 生成历史预测记录。");
        return ApiResponse.ok(hint);
    }

    /**
     * GET /api/backtest/symbols — 返回数据库中所有可用品种及其数据日期范围。
     */
    @GetMapping("/symbols")
    public ApiResponse<Map<String, Object>> symbols() {
        return ApiResponse.ok(backtestService.getAvailableSymbols());
    }

    /**
     * POST /api/backtest/import-predictions — 批量导入历史预测数据。
     *
     * <p>解决 AND/VETO/ModelOnly 策略无预测数据的问题。请求体示例：
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
     * <p>数据来源可以是：
     * <ul>
     *   <li>Python 脚本 ensemble.csv / gbo_tft_test_predictions_*.csv 的 y_pred 列</li>
     *   <li>模型服务批量推理的输出</li>
     *   <li>任何格式的历史预测，只需整理成上述 JSON 格式</li>
     * </ul>
     *
     * <p>幂等操作：同一 target+horizon+date 已存在时自动跳过，不会重复写入。
     */
    @PostMapping("/import-predictions")
    public ApiResponse<Map<String, Object>> importPredictions(
            @RequestBody PredictionImportRequest request) {
        return ApiResponse.ok(backtestService.importPredictions(request));
    }

    /**
     * POST /api/backtest/run — 执行策略回测。
     *
     * <p>请求体示例：
     * <pre>
     * {
     *   "symbol": "LCO1",
     *   "startDate": "2022-01-01",
     *   "endDate": "2024-12-31",
     *   "strategies": ["Aberration", "MACD"],
     *   "combineModes": ["baseOnly", "AND"],
     *   "feeSlipRatePerSide": 0.0005
     * }
     * </pre>
     *
     * <p>响应包含：
     * <ul>
     *   <li>{@code dataInfo} — 数据概览（OHLCV 条数、ML 预测覆盖情况、说明）</li>
     *   <li>{@code results} — 每个策略的完整指标（胜率、回撤、盈亏比、样本外指标、净值曲线、成本敏感性）</li>
     * </ul>
     */
    @PostMapping("/run")
    public ApiResponse<BacktestResponse> run(@RequestBody BacktestRequest request) {
        return ApiResponse.ok(backtestService.runBacktest(request));
    }
}
