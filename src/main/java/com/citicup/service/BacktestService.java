package com.citicup.service;

import com.citicup.dto.backtest.*;
import com.citicup.entity.OilPriceDailyOhlcv;
import com.citicup.entity.PredictionRun;
import com.citicup.repository.OilPriceDailyOhlcvRepo;
import com.citicup.repository.PredictionRunRepo;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.LocalDate;
import java.util.*;

/**
 * 策略回测核心服务。
 *
 * <p>将 ~/model/backtest_ensemble_strategies.py 中的回测逻辑以纯 Java 重新实现，
 * 数据直接从数据库读取（oil_price_daily_ohlcv + prediction_run），无需外部 CSV 文件。
 *
 * <p>支持的基础策略：Aberration（布林带）、DualThrust（双轨突破）、MACD（金叉死叉）、Momentum（动量）。
 * 支持的组合模式：baseOnly（纯技术）、AND（与 ML 信号取交集）、VETO（ML 主导，基础策略否决）。
 */
@Service
@RequiredArgsConstructor
public class BacktestService {

    private static final Logger log = LoggerFactory.getLogger(BacktestService.class);

    private final OilPriceDailyOhlcvRepo ohlcvRepo;
    private final PredictionRunRepo predRunRepo;
    private final ObjectMapper objectMapper;

    // =========================================================================
    // Public API
    // =========================================================================

    /**
     * 执行策略回测，返回所有请求策略的完整绩效指标和净值曲线。
     */
    public BacktestResponse runBacktest(BacktestRequest req) {
        // 1. 加载 OHLCV 历史数据
        List<OilPriceDailyOhlcv> ohlcvList = loadOhlcv(req.getSymbol(), req.getStartDate(), req.getEndDate());
        if (ohlcvList.isEmpty()) {
            throw new IllegalArgumentException(
                    "数据库中未找到品种 [" + req.getSymbol() + "] 的 OHLCV 数据，" +
                    "请调用 GET /api/backtest/symbols 确认可用品种。");
        }

        int n = ohlcvList.size();
        double[] open  = new double[n];
        double[] close = new double[n];
        double[] high  = new double[n];
        double[] low   = new double[n];
        LocalDate[] dates = new LocalDate[n];

        for (int i = 0; i < n; i++) {
            OilPriceDailyOhlcv bar = ohlcvList.get(i);
            dates[i] = bar.getTradeDate();
            open[i]  = bar.getOpenPrice();
            close[i] = bar.getClosePrice();
            high[i]  = bar.getHighPrice();
            low[i]   = bar.getLowPrice();
        }

        // 2. 尝试加载 ML 预测数据
        Map<LocalDate, Double> mlPredMap = loadMlPredictions(req.getSymbol());
        double[] predArr = buildPredArray(dates, mlPredMap);
        int overlapCount = countNonNan(predArr);

        // 3. 构建数据信息摘要
        BacktestDataInfo dataInfo = BacktestDataInfo.builder()
                .symbol(req.getSymbol())
                .totalBars(n)
                .dataStartDate(dates[0].toString())
                .dataEndDate(dates[n - 1].toString())
                .mlPredictionsAvailable(!mlPredMap.isEmpty())
                .mlPredictionCount(mlPredMap.size())
                .overlappingBars(overlapCount)
                .note(buildNote(n, mlPredMap.isEmpty(), overlapCount))
                .build();

        // 4. 解析请求中的策略和模式列表
        Set<String> strats = normalizeSet(req.getStrategies(),
                Set.of("aberration", "dualthrust", "macd", "momentum", "modelonly"));
        Set<String> modes = normalizeSet(req.getCombineModes(),
                Set.of("baseonly", "and", "veto"));

        List<StrategyBacktestResult> results = new ArrayList<>();

        // 5. 计算各技术策略的方向信号（at-bar；随后 shift(1) 避免未来数据）
        Map<String, int[]> baseSignals = new LinkedHashMap<>();
        if (strats.contains("aberration"))
            baseSignals.put("Aberration",
                    computeAberrationDirection(close, 35, 1.0, 1.0));
        if (strats.contains("dualthrust"))
            baseSignals.put("DualThrust",
                    computeDualThrustDirection(open, high, low, close, 20, 0.5));
        if (strats.contains("macd"))
            baseSignals.put("MACD",
                    computeMacdDirection(close, 12, 26, 9));
        if (strats.contains("momentum"))
            baseSignals.put("Momentum",
                    computeMomentumDirection(close, 3, 10));

        for (Map.Entry<String, int[]> entry : baseSignals.entrySet()) {
            String sName = entry.getKey();
            // shift(1)：用 t-1 时刻的信号在 t 时刻开仓，防止信息泄漏
            int[] baseDirForTrade = shiftByOne(entry.getValue());

            if (modes.contains("baseonly")) {
                results.add(runSingle(sName + "(baseOnly)", dates, open, close,
                        baseDirForTrade, req.getFeeSlipRatePerSide()));
            }
            if (modes.contains("and")) {
                int[] andDir = andCombine(baseDirForTrade, predArr, open);
                results.add(runSingle(sName + "+Model(AND)", dates, open, close,
                        andDir, req.getFeeSlipRatePerSide()));
            }
            if (modes.contains("veto")) {
                int[] vetoDir = vetoCombine(baseDirForTrade, predArr, open);
                results.add(runSingle(sName + "+Model(VETO)", dates, open, close,
                        vetoDir, req.getFeeSlipRatePerSide()));
            }
        }

        // 6. 纯模型策略（Model-only）
        if (strats.contains("modelonly")) {
            int[] modelDir = modelOnlyDir(predArr, open);
            results.add(runSingle("Model(only)", dates, open, close,
                    modelDir, req.getFeeSlipRatePerSide()));
        }

        return BacktestResponse.builder()
                .dataInfo(dataInfo)
                .results(results)
                .build();
    }

    /**
     * 批量导入历史预测数据。
     *
     * <p>每条预测以一条独立的 {@code prediction_run} 记录存储，{@code runAt} 设为目标日期当天零点（UTC），
     * 便于后续回测时按 runAt 顺序重建预测序列。同一 target+horizon+date 若已存在记录则跳过（不覆盖），
     * 避免重复导入。
     *
     * @return 包含 inserted（新写入数量）、skipped（已存在跳过数量）的统计 Map
     */
    public Map<String, Object> importPredictions(PredictionImportRequest req) {
        if (req.getPredictions() == null || req.getPredictions().isEmpty()) {
            throw new IllegalArgumentException("predictions 列表不能为空");
        }

        // target 统一大写，与数据库保持一致（WTI / BRENT）
        String target  = (req.getTarget()  != null ? req.getTarget()  : "WTI").toUpperCase();
        String horizon = req.getHorizon() != null ? req.getHorizon() : "1d";

        // 查出已有记录的 runAt 时间戳集合，用于去重
        List<PredictionRun> existing = predRunRepo.findByTargetIgnoreCaseAndHorizonOrderByRunAtAsc(target, horizon);
        Set<Instant> existingRunAts = new HashSet<>();
        for (PredictionRun pr : existing) {
            existingRunAts.add(pr.getRunAt());
        }

        int inserted = 0, skipped = 0;
        List<PredictionRun> toSave = new ArrayList<>();

        for (PredictionImportRequest.PredictionEntry entry : req.getPredictions()) {
            if (entry.getDate() == null || entry.getDate().isBlank()) continue;

            LocalDate targetDate;
            try {
                targetDate = LocalDate.parse(entry.getDate().trim());
            } catch (Exception e) {
                log.warn("跳过格式错误的日期：{}", entry.getDate());
                skipped++;
                continue;
            }

            // 以目标日期的 UTC 午夜作为 runAt，使其唯一标识一个"为某天生成的预测"
            Instant runAt = targetDate.atStartOfDay(java.time.ZoneOffset.UTC).toInstant();
            if (existingRunAts.contains(runAt)) {
                skipped++;
                continue;
            }

            String forecastJson;
            try {
                // 存储为标准格式，与模型服务输出兼容
                forecastJson = objectMapper.writeValueAsString(Map.of(
                        "target", target,
                        "horizon", horizon,
                        "predictions", List.of(Map.of("date", targetDate.toString(), "value", entry.getValue()))
                ));
            } catch (Exception e) {
                log.warn("序列化预测条目失败，跳过 date={}: {}", entry.getDate(), e.getMessage());
                skipped++;
                continue;
            }

            toSave.add(PredictionRun.builder()
                    .target(target)
                    .horizon(horizon)
                    .runAt(runAt)
                    .forecastJson(forecastJson)
                    .build());
            existingRunAts.add(runAt); // 防止同一请求内重复
            inserted++;
        }

        if (!toSave.isEmpty()) {
            predRunRepo.saveAll(toSave);
        }

        log.info("预测导入完成：target={} horizon={} inserted={} skipped={}", target, horizon, inserted, skipped);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("target", target);
        result.put("horizon", horizon);
        result.put("inserted", inserted);
        result.put("skipped", skipped);
        result.put("total", req.getPredictions().size());
        return result;
    }

    /**
     * 返回数据库中可用的品种列表及各品种的日期范围，方便前端初始化选项。
     */
    public Map<String, Object> getAvailableSymbols() {
        List<String> symbols = ohlcvRepo.findDistinctSymbols();
        List<Map<String, Object>> list = new ArrayList<>();
        for (String sym : symbols) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("symbol", sym);
            m.put("startDate", ohlcvRepo.findMinDateBySymbol(sym)
                    .map(LocalDate::toString).orElse(null));
            m.put("endDate", ohlcvRepo.findMaxDateBySymbol(sym)
                    .map(LocalDate::toString).orElse(null));
            list.add(m);
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("symbols", list);
        result.put("count", list.size());
        return result;
    }

    // =========================================================================
    // Data Loading
    // =========================================================================

    private List<OilPriceDailyOhlcv> loadOhlcv(String symbol, LocalDate startDate, LocalDate endDate) {
        if (startDate != null && endDate != null) {
            return ohlcvRepo.findBySymbolAndTradeDateBetweenOrderByTradeDateAsc(symbol, startDate, endDate);
        }
        return ohlcvRepo.findBySymbolOrderByTradeDateAsc(symbol);
    }

    /**
     * 从 prediction_run 表重建 date→predictedClose 映射。
     *
     * <p>原理：对每条 horizon="1d" 的预测记录，解析 forecastJson 中的 predictions 数组，
     * 将 {"date": "YYYY-MM-DD", "value": ...} 映射到对应日期。
     * 若同一日期存在多条预测，保留最新一条（因按 runAt 升序排列，后者覆盖前者）。
     *
     * <p>若 forecastJson 格式不符或字段缺失，跳过该记录并记录 debug 日志。
     */
    private Map<LocalDate, Double> loadMlPredictions(String symbol) {
        // symbol → target 映射，统一大写，与数据库中的 target 字段做大小写不敏感匹配
        // LCO1（布伦特）→ BRENT；WTI/CL 系列 → WTI
        String sym = symbol.toUpperCase();
        String target = (sym.contains("WTI") || sym.startsWith("CL")) ? "WTI" : "BRENT";

        List<PredictionRun> runs = predRunRepo.findByTargetIgnoreCaseAndHorizonOrderByRunAtAsc(target, "1d");
        Map<LocalDate, Double> result = new LinkedHashMap<>();

        for (PredictionRun run : runs) {
            if (run.getForecastJson() == null || run.getForecastJson().isBlank()) continue;
            try {
                parseForecastJson(run.getForecastJson(), result);
            } catch (Exception e) {
                log.debug("解析 prediction_run id={} 的 forecastJson 失败，跳过: {}",
                        run.getId(), e.getMessage());
            }
        }

        log.info("品种 {} (target={}) 共加载 {} 条 ML 预测记录", symbol, target, result.size());
        return result;
    }

    /**
     * 解析 forecastJson，支持两种格式：
     * <ul>
     *   <li>格式 A（旧版模型服务）：{@code {"point":[{"t":"2026-03-11T00:00:00Z","v":73.1}],...}}</li>
     *   <li>格式 B（新版/导入）：{@code {"predictions":[{"date":"2026-03-11","value":73.1}]}}</li>
     * </ul>
     */
    private static void parseForecastJson(String json, Map<LocalDate, Double> out)
            throws Exception {
        JsonNode root = OBJECT_MAPPER_STATIC.readTree(json);

        // 格式 B：predictions[].date / .value
        JsonNode preds = root.get("predictions");
        if (preds != null && preds.isArray()) {
            for (JsonNode p : preds) {
                JsonNode dateNode  = p.get("date");
                JsonNode valueNode = p.get("value");
                if (dateNode == null || valueNode == null) continue;
                out.put(LocalDate.parse(dateNode.asText().substring(0, 10)),
                        valueNode.asDouble());
            }
            return;
        }

        // 格式 A：point[].t (ISO-8601) / .v
        JsonNode point = root.get("point");
        if (point != null && point.isArray()) {
            for (JsonNode p : point) {
                JsonNode tNode = p.get("t");
                JsonNode vNode = p.get("v");
                if (tNode == null || vNode == null) continue;
                // t 可能是 "2026-03-11T00:00:00Z"，取前 10 位即日期
                out.put(LocalDate.parse(tNode.asText().substring(0, 10)),
                        vNode.asDouble());
            }
        }
    }

    // 静态 ObjectMapper 供静态方法使用（Spring 注入的 objectMapper 不可用于静态上下文）
    private static final ObjectMapper OBJECT_MAPPER_STATIC = new ObjectMapper();

    /** 将日期→预测值的 Map 对齐到 OHLCV 日期数组，无预测的位置填 NaN */
    private static double[] buildPredArray(LocalDate[] dates, Map<LocalDate, Double> predMap) {
        double[] arr = new double[dates.length];
        Arrays.fill(arr, Double.NaN);
        for (int i = 0; i < dates.length; i++) {
            Double v = predMap.get(dates[i]);
            if (v != null) arr[i] = v;
        }
        return arr;
    }

    private static int countNonNan(double[] arr) {
        int count = 0;
        for (double v : arr) if (!Double.isNaN(v)) count++;
        return count;
    }

    // =========================================================================
    // Technical Indicator Signal Computation
    // =========================================================================

    /**
     * 指数移动平均（EWM），alpha = 2/(span+1)，adjust=False，与 pandas 默认行为一致。
     */
    private static double[] ema(double[] x, int span) {
        double alpha = 2.0 / (span + 1);
        double decay = 1.0 - alpha;
        double[] result = new double[x.length];
        if (x.length == 0) return result;
        result[0] = x[0];
        for (int i = 1; i < x.length; i++) {
            result[i] = alpha * x[i] + decay * result[i - 1];
        }
        return result;
    }

    /**
     * Aberration（布林带通道突破）方向信号。
     * MA = 滚动均值(window)；Std = 滚动标准差(ddof=0)
     * +1: close > MA + stdUp*Std；-1: close < MA - stdDn*Std；0: 区间内
     */
    private static int[] computeAberrationDirection(
            double[] close, int window, double stdUp, double stdDn) {
        int n = close.length;
        int[] dir = new int[n];
        for (int i = window - 1; i < n; i++) {
            double sum = 0, sumSq = 0;
            for (int j = i - window + 1; j <= i; j++) {
                sum   += close[j];
                sumSq += close[j] * close[j];
            }
            double ma  = sum / window;
            double std = Math.sqrt(Math.max(0, sumSq / window - ma * ma));
            if (close[i] > ma + stdUp * std) dir[i] = 1;
            else if (close[i] < ma - stdDn * std) dir[i] = -1;
        }
        return dir;
    }

    /**
     * Dual Thrust（双轨突破）方向信号。
     * HH = max(high,N)；LC = min(close,N)；HC = max(close,N)；LL = min(low,N)
     * Range = max(HH-LC, HC-LL)；upper = open + k*Range；lower = open - k*Range
     */
    private static int[] computeDualThrustDirection(
            double[] open, double[] high, double[] low, double[] close,
            int window, double k) {
        int n = close.length;
        int[] dir = new int[n];
        for (int i = window - 1; i < n; i++) {
            double hh = Double.NEGATIVE_INFINITY, lc = Double.POSITIVE_INFINITY;
            double hc = Double.NEGATIVE_INFINITY, ll = Double.POSITIVE_INFINITY;
            for (int j = i - window + 1; j <= i; j++) {
                if (high[j]  > hh) hh = high[j];
                if (close[j] < lc) lc = close[j];
                if (close[j] > hc) hc = close[j];
                if (low[j]   < ll) ll = low[j];
            }
            double rng   = Math.max(hh - lc, hc - ll);
            double upper = open[i] + k * rng;
            double lower = open[i] - k * rng;
            if (close[i] > upper) dir[i] = 1;
            else if (close[i] < lower) dir[i] = -1;
        }
        return dir;
    }

    /**
     * MACD（金叉/死叉）方向信号。
     * DIF = EMA(fast) - EMA(slow)；DEA = EMA(DIF, signal)
     * 金叉（DIF 从下方穿越 DEA）=> +1；死叉 => -1
     */
    private static int[] computeMacdDirection(
            double[] close, int fast, int slow, int signal) {
        double[] emaFast = ema(close, fast);
        double[] emaSlow = ema(close, slow);
        int n = close.length;
        double[] dif = new double[n];
        for (int i = 0; i < n; i++) dif[i] = emaFast[i] - emaSlow[i];
        double[] dea = ema(dif, signal);
        int[] dir = new int[n];
        for (int i = 1; i < n; i++) {
            if (dif[i - 1] <= dea[i - 1] && dif[i] > dea[i]) dir[i] =  1;
            else if (dif[i - 1] >= dea[i - 1] && dif[i] < dea[i]) dir[i] = -1;
        }
        return dir;
    }

    /**
     * Momentum（动量）方向信号。
     * shortRet = close[t] - close[t - shortN]；longRet = close[t] - close[t - longN]
     * 两者符号一致 => 顺势；不一致 => 取长期符号（反转逻辑）
     */
    private static int[] computeMomentumDirection(double[] close, int shortN, int longN) {
        int n = close.length;
        int[] dir = new int[n];
        for (int i = longN; i < n; i++) {
            int sShort = signum(close[i] - close[i - shortN]);
            int sLong  = signum(close[i] - close[i - longN]);
            if (sShort == 0 || sLong == 0) dir[i] = 0;
            else dir[i] = (sShort == sLong) ? sShort : sLong;
        }
        return dir;
    }

    private static int signum(double v) {
        if (v > 0) return 1;
        if (v < 0) return -1;
        return 0;
    }

    /**
     * 将信号序列向后移一位（shift(1)，以 NaN=0 填充首位），
     * 确保 t-1 时刻的信号在 t 时刻执行，避免未来数据泄漏。
     */
    private static int[] shiftByOne(int[] dir) {
        int[] shifted = new int[dir.length];
        // shifted[0] = 0（默认）
        System.arraycopy(dir, 0, shifted, 1, dir.length - 1);
        return shifted;
    }

    // =========================================================================
    // Combination Rules
    // =========================================================================

    /**
     * AND 规则：技术信号与 ML 模型信号方向完全一致时才交易。
     * 若无 ML 预测（NaN）=> 模型方向为 0 => AND 结果为 0（不交易）。
     */
    private static int[] andCombine(int[] baseDir, double[] pred, double[] open) {
        int n = baseDir.length;
        int[] finalDir = new int[n];
        for (int i = 0; i < n; i++) {
            int modelDir = modelDirection(pred[i], open[i]);
            finalDir[i] = (baseDir[i] == modelDir) ? baseDir[i] : 0;
        }
        return finalDir;
    }

    /**
     * VETO 规则：默认跟随 ML 模型方向交易；
     * 仅当技术策略给出明确的反向信号时才否决（不交易）。
     * 若无 ML 预测 => 模型方向为 0 => 无交易。
     */
    private static int[] vetoCombine(int[] baseDir, double[] pred, double[] open) {
        int n = baseDir.length;
        int[] finalDir = new int[n];
        for (int i = 0; i < n; i++) {
            int modelDir = modelDirection(pred[i], open[i]);
            boolean contradict = (baseDir[i] != 0) && (baseDir[i] != modelDir);
            finalDir[i] = contradict ? 0 : modelDir;
        }
        return finalDir;
    }

    /** 纯 ML 模型方向（不叠加技术策略）。 */
    private static int[] modelOnlyDir(double[] pred, double[] open) {
        int n = pred.length;
        int[] dir = new int[n];
        for (int i = 0; i < n; i++) dir[i] = modelDirection(pred[i], open[i]);
        return dir;
    }

    /** pred > open => +1（做多）；pred < open => -1（做空）；NaN 或相等 => 0（不交易）。 */
    private static int modelDirection(double pred, double open) {
        if (Double.isNaN(pred)) return 0;
        if (pred > open) return  1;
        if (pred < open) return -1;
        return 0;
    }

    // =========================================================================
    // Single Strategy Execution & Metrics
    // =========================================================================

    private StrategyBacktestResult runSingle(
            String name, LocalDate[] dates, double[] open, double[] close,
            int[] finalDir, double feeRate) {

        int n = dates.length;
        if (n == 0) {
            return StrategyBacktestResult.builder()
                    .strategyName(name)
                    .equityCurve(Collections.emptyList())
                    .costSensitivity(Collections.emptyList())
                    .build();
        }

        // --- 日收益率 ---
        double[] dailyRet = new double[n];
        for (int i = 0; i < n; i++) {
            if (finalDir[i] == 1)       dailyRet[i] = (close[i] - open[i]) / open[i];
            else if (finalDir[i] == -1) dailyRet[i] = (open[i] - close[i]) / open[i];
        }

        // --- 累计净值曲线 ---
        double[] equity = new double[n];
        double cum = 1.0;
        for (int i = 0; i < n; i++) {
            cum *= (1.0 + dailyRet[i]);
            equity[i] = cum;
        }

        // --- 交易统计 ---
        int nTrades = 0, wins = 0, losses = 0;
        double winSum = 0, lossSum = 0, retSum = 0;
        for (int i = 0; i < n; i++) {
            if (finalDir[i] != 0) {
                nTrades++;
                retSum += dailyRet[i];
                if      (dailyRet[i] > 0) { wins++;   winSum  += dailyRet[i]; }
                else if (dailyRet[i] < 0) { losses++; lossSum += dailyRet[i]; }
            }
        }
        double winRate   = nTrades > 0 ? (double) wins / nTrades : 0;
        double avgRet    = nTrades > 0 ? retSum / nTrades : 0;
        double avgWin    = wins    > 0 ? winSum  / wins   : 0;
        double avgLoss   = losses  > 0 ? lossSum / losses : 0;
        double lossAbs   = Math.abs(lossSum);
        double pf        = lossAbs > 1e-15 ? winSum / lossAbs : (wins > 0 ? 999.0 : 0.0);
        double totalRet  = equity[n - 1] - 1.0;
        double maxDd     = maxDrawdown(equity);

        // --- 样本外（后 20%）指标 ---
        int splitIdx = (int) Math.ceil(n * 0.8);
        double startEq   = splitIdx > 0 ? equity[splitIdx - 1] : 1.0;
        double oosRet    = equity[n - 1] / startEq - 1.0;
        int oosWins = 0, oosTrades = 0;
        for (int i = splitIdx; i < n; i++) {
            if (finalDir[i] != 0) {
                oosTrades++;
                if (dailyRet[i] > 0) oosWins++;
            }
        }
        double oosWinRate = oosTrades > 0 ? (double) oosWins / oosTrades : 0;
        double oosPeak = startEq, oosMaxDd = 0;
        for (int i = splitIdx - 1; i < n; i++) {
            if (equity[i] > oosPeak) oosPeak = equity[i];
            double dd = equity[i] / oosPeak - 1.0;
            if (dd < oosMaxDd) oosMaxDd = dd;
        }

        // --- 63 日滚动最大回撤（Python 中 min_periods=10） ---
        double worstRdd = 0;
        for (int i = 9; i < n; i++) {
            int windowStart = Math.max(0, i - 62);
            double windowMax = 0;
            for (int j = windowStart; j <= i; j++) {
                if (equity[j] > windowMax) windowMax = equity[j];
            }
            if (windowMax > 0) {
                double dd = equity[i] / windowMax - 1.0;
                if (dd < worstRdd) worstRdd = dd;
            }
        }

        // --- 净值曲线列表 ---
        List<EquityPoint> equityCurve = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            equityCurve.add(new EquityPoint(dates[i].toString(), r4(equity[i])));
        }

        // --- 成本敏感性分析（x1/x2/x3 费率倍数） ---
        List<CostSensitivityPoint> costSens = new ArrayList<>(3);
        for (double mult : new double[]{1.0, 2.0, 3.0}) {
            double cost = feeRate * mult;
            double netCum = 1.0;
            double[] netEq = new double[n];
            for (int i = 0; i < n; i++) {
                double netRet = (finalDir[i] != 0) ? dailyRet[i] - 2.0 * cost : 0.0;
                netCum *= (1.0 + netRet);
                netEq[i] = netCum;
            }
            costSens.add(new CostSensitivityPoint(mult, r4(netEq[n - 1] - 1.0), r4(maxDrawdown(netEq))));
        }

        return StrategyBacktestResult.builder()
                .strategyName(name)
                .nTrades(nTrades)
                .winRate(r4(winRate))
                .totalReturn(r4(totalRet))
                .maxDrawdown(r4(maxDd))
                .avgReturnPerTrade(r4(avgRet))
                .avgWin(r4(avgWin))
                .avgLoss(r4(avgLoss))
                .profitFactor(r4(pf))
                .oosReturn(r4(oosRet))
                .oosWinRate(r4(oosWinRate))
                .oosMaxDrawdown(r4(oosMaxDd))
                .worstRollingDrawdown63d(r4(worstRdd))
                .equityCurve(equityCurve)
                .costSensitivity(costSens)
                .build();
    }

    // =========================================================================
    // Utility
    // =========================================================================

    private static double maxDrawdown(double[] equity) {
        double peak = 0, maxDd = 0;
        for (double v : equity) {
            if (v > peak) peak = v;
            if (peak > 0) {
                double dd = v / peak - 1.0;
                if (dd < maxDd) maxDd = dd;
            }
        }
        return maxDd;
    }

    /** 四舍五入保留 4 位小数；Infinity 用 ±999 代替（避免 JSON 序列化问题）。 */
    private static double r4(double v) {
        if (Double.isNaN(v))       return 0.0;
        if (Double.isInfinite(v))  return v > 0 ? 999.0 : -999.0;
        return Math.round(v * 10000.0) / 10000.0;
    }

    /** 将字符串列表规范化为小写 Set；输入为 null/空时返回 defaults（全选）。 */
    private static Set<String> normalizeSet(List<String> input, Set<String> defaults) {
        if (input == null || input.isEmpty()) return defaults;
        Set<String> result = new HashSet<>();
        for (String s : input) result.add(s.toLowerCase().trim());
        return result;
    }

    private static String buildNote(int n, boolean noMlPred, int overlapCount) {
        if (n < 35) {
            return "警告：OHLCV 数据不足 35 条，Aberration 策略无法生成有效信号（需要至少 35 个交易日）。";
        }
        if (noMlPred) {
            return "ML 预测数据未找到：AND / VETO / ModelOnly 策略无交易信号（等效空仓），仅 baseOnly 策略有效。" +
                   "如需 ML 策略回测，请先多次调用 POST /api/predict（horizon=1d）积累历史预测记录。";
        }
        if (overlapCount == 0) {
            return "找到 ML 预测记录，但预测日期与 OHLCV 日期无重叠。" +
                   "请检查 prediction_run 中 forecastJson 的 date 字段是否与 OHLCV 日期匹配。";
        }
        if (overlapCount < 10) {
            return "ML 预测与 OHLCV 重叠数据点较少（" + overlapCount +
                   " 条），AND/VETO/ModelOnly 策略信号稀疏，结果仅供参考。";
        }
        return "数据正常：共 " + n + " 条 OHLCV，ML 预测覆盖其中 " + overlapCount + " 个交易日。";
    }
}
