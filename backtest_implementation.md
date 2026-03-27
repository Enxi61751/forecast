# 策略回测模块实现说明

## 一、功能概述

本模块将 `~/model/backtest_ensemble_strategies.py` 中的回测逻辑以纯 Java 重新实现，直接从数据库读取历史数据，通过 REST API 向前端暴露。核心能力：

- 使用真实历史 OHLCV 数据，模拟四种技术策略在过去每个交易日的买卖信号
- 支持三种组合模式：纯技术信号（baseOnly）、与 ML 模型取交集（AND）、ML 主导/技术否决（VETO）
- 输出每日净值曲线、完整绩效指标、样本外指标、成本敏感性分析

---

## 二、代码结构

```
src/main/java/com/citicup/
├── dto/backtest/
│   ├── BacktestRequest.java          请求参数
│   ├── BacktestResponse.java         响应包装
│   ├── BacktestDataInfo.java         数据可用性摘要
│   ├── StrategyBacktestResult.java   单策略完整结果
│   ├── EquityPoint.java              净值曲线数据点
│   ├── CostSensitivityPoint.java     成本敏感性数据点
│   └── PredictionImportRequest.java  批量导入预测的请求体
├── service/
│   └── BacktestService.java          核心回测逻辑
├── controller/
│   └── BacktestController.java       REST API
└── repository/
    ├── OilPriceDailyOhlcvRepo.java   新增 DISTINCT/MIN/MAX 查询
    └── PredictionRunRepo.java        新增大小写不敏感的 target 查询
```

---

## 三、数据来源

### 3.1 OHLCV 历史价格数据（已确认可用）

- **表**：`oil_price_daily_ohlcv`
- **实际数据**：**5386 条**，品种 `LCO1`（布伦特原油），日期范围 **2006-01-03 ~ 2026-02-20**
- **查询方式**：`findBySymbolAndTradeDateBetweenOrderByTradeDateAsc`（指定日期范围）或 `findBySymbolOrderByTradeDateAsc`（全量）
- **注意**：目前数据库中只有 `LCO1` 这一个品种，回测请求的 `symbol` 字段请填 `"LCO1"`

### 3.2 ML 模型预测数据（用于 AND/VETO/ModelOnly 策略）

- **表**：`prediction_run`
- **实际数据**：当前共 **7 条**，全部为 2026-03 之后的**未来预测**，与历史 OHLCV 日期**无重叠**
- **提取逻辑**：查询 `horizon="1d"` 的记录，按 target 大小写不敏感匹配（`UPPER(target) = UPPER(:target)`），解析 `forecastJson`

`forecastJson` 兼容两种格式：

**格式 A**（旧版模型服务输出）：
```json
{"point":[{"t":"2026-03-11T00:00:00Z","v":73.1}],"lower":null,"upper":null,"raw":{"lgbm":73.1,"tft":73.1}}
```

**格式 B**（新版/导入格式）：
```json
{"predictions":[{"date":"2026-03-11","value":73.1}]}
```

两种格式均可被正确解析，提取 `日期 → 预测收盘价` 映射后对齐到 OHLCV 日期数组，无预测的位置填 `NaN`（视为无信号）。

**symbol → target 映射规则**（大小写不敏感）：
- `LCO1`（布伦特）→ `BRENT`
- `WTI`、`CL` 开头 → `WTI`

---

## 四、策略说明

所有策略均使用 **t-1 时刻的信号在 t 时刻执行**（`shift(1)`），避免未来数据泄漏。

### 4.1 Aberration（布林带通道突破）

| 参数 | 值 |
|------|----|
| window | 35 |
| std_up / std_dn | 1.0 / 1.0 |

- MA = 35 日滚动均值；Std = 35 日滚动标准差（ddof=0）
- close > MA + Std → 做多(+1)
- close < MA − Std → 做空(-1)
- 区间内 → 观望(0)

### 4.2 DualThrust（双轨突破）

| 参数 | 值 |
|------|----|
| window | 20 |
| k | 0.5 |

- HH = max(high, 20d)，LC = min(close, 20d)，HC = max(close, 20d)，LL = min(low, 20d)
- Range = max(HH−LC, HC−LL)
- close > open + k×Range → 做多；close < open − k×Range → 做空

### 4.3 MACD（金叉/死叉）

| 参数 | 值 |
|------|----|
| fast / slow / signal | 12 / 26 / 9 |

- DIF = EMA(12) − EMA(26)；DEA = EMA(DIF, 9)（均为 adjust=False EWM）
- DIF 从下方穿越 DEA（金叉）→ +1；从上方穿越（死叉）→ -1

### 4.4 Momentum（动量）

| 参数 | 值 |
|------|----|
| short_n / long_n | 3 / 10 |

- shortRet = close[t] − close[t−3]；longRet = close[t] − close[t−10]
- 两者方向一致 → 顺势；方向相反 → 取长期方向（反转逻辑）

### 4.5 组合模式

| 模式 | 逻辑 |
|------|------|
| **baseOnly** | 纯技术信号，不使用 ML 预测 |
| **AND** | 技术信号与 ML 信号方向一致时才交易；无预测（NaN）→ 不交易 |
| **VETO** | 默认跟随 ML 信号；技术策略给出明确反向信号时否决；无预测 → 不交易 |
| **ModelOnly** | 完全由 ML 预测决定方向（pred > open → 做多，pred < open → 做空） |

---

## 五、绩效指标说明

| 指标 | 含义 |
|------|------|
| nTrades | 有持仓信号的总交易日数 |
| winRate | 盈利交易日 / 总交易日 |
| totalReturn | 全样本累计收益率（小数，如 0.23 = +23%） |
| maxDrawdown | 全样本最大回撤（负数小数） |
| avgReturnPerTrade | 每笔交易平均收益率 |
| avgWin / avgLoss | 盈利/亏损交易的平均收益率 |
| profitFactor | 总盈利 / 总亏损绝对值；无亏损时为 999 |
| oosReturn | 样本外（后 20%）总收益率 |
| oosWinRate | 样本外胜率 |
| oosMaxDrawdown | 样本外最大回撤 |
| worstRollingDrawdown63d | 全样本内 63 日滚动窗口最差最大回撤 |
| equityCurve | 每日净值数组（初始值 1.0） |
| costSensitivity | 1×/2×/3× 费率倍数下的扣费后净收益和最大回撤 |

**收益率计算方式**：日内交易，以当日开盘价买入/做空，当日收盘价平仓：
- 做多：`(close − open) / open`
- 做空：`(open − close) / open`

---

## 六、API 参考

### GET /api/backtest/symbols

返回数据库中所有可用品种及其数据日期范围：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "count": 1,
    "symbols": [
      {"symbol": "LCO1", "startDate": "2006-01-03", "endDate": "2026-02-20"}
    ]
  }
}
```

### POST /api/backtest/run

**请求体（JSON）：**

```json
{
  "symbol": "LCO1",
  "startDate": "2022-01-01",
  "endDate": "2024-12-31",
  "strategies": ["Aberration", "DualThrust", "MACD", "Momentum"],
  "combineModes": ["baseOnly"],
  "feeSlipRatePerSide": 0.0005
}
```

| 字段 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| symbol | 否 | `"LCO1"` | 与数据库 `oil_price_daily_ohlcv.symbol` 完全一致 |
| startDate / endDate | 否 | 全量 | 不填则使用该品种全部历史数据 |
| strategies | 否 | 全部 | 可选：Aberration、DualThrust、MACD、Momentum、ModelOnly |
| combineModes | 否 | 全部 | 可选：baseOnly、AND、VETO |
| feeSlipRatePerSide | 否 | `0.0005` | 仅影响 costSensitivity 字段 |

**响应体示例（简化）：**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "dataInfo": {
      "symbol": "LCO1",
      "totalBars": 756,
      "dataStartDate": "2022-01-03",
      "dataEndDate": "2024-12-31",
      "mlPredictionsAvailable": false,
      "mlPredictionCount": 0,
      "overlappingBars": 0,
      "note": "ML 预测数据未找到：AND/VETO/ModelOnly 策略无交易信号..."
    },
    "results": [
      {
        "strategyName": "Aberration(baseOnly)",
        "nTrades": 184,
        "winRate": 0.5163,
        "totalReturn": 0.1823,
        "maxDrawdown": -0.1142,
        "avgReturnPerTrade": 0.001,
        "avgWin": 0.0082,
        "avgLoss": -0.0063,
        "profitFactor": 1.6734,
        "oosReturn": 0.0341,
        "oosWinRate": 0.5,
        "oosMaxDrawdown": -0.0712,
        "worstRollingDrawdown63d": -0.0953,
        "equityCurve": [
          {"date": "2022-01-03", "equity": 1.0},
          {"date": "2022-01-04", "equity": 1.0023}
        ],
        "costSensitivity": [
          {"costMultiplier": 1.0, "netTotalReturn": 0.1636, "netMaxDrawdown": -0.1201},
          {"costMultiplier": 2.0, "netTotalReturn": 0.1449, "netMaxDrawdown": -0.126},
          {"costMultiplier": 3.0, "netTotalReturn": 0.1262, "netMaxDrawdown": -0.132}
        ]
      }
    ]
  }
}
```

### POST /api/backtest/import-predictions

批量导入历史预测数据，写入 `prediction_run` 表，用于解锁 AND/VETO/ModelOnly 策略。幂等操作，同一 target+horizon+date 已存在时自动跳过。

**请求体（JSON）：**

```json
{
  "target": "BRENT",
  "horizon": "1d",
  "predictions": [
    {"date": "2022-01-04", "value": 75.3},
    {"date": "2022-01-05", "value": 74.8}
  ]
}
```

**响应体：**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "target": "BRENT",
    "horizon": "1d",
    "inserted": 2,
    "skipped": 0,
    "total": 2
  }
}
```

---

## 七、当前能否正常运行？

> 以下结论基于 2026-03-27 实际查询数据库的结果。

### ✅ 立即可用

**baseOnly 策略（Aberration / DualThrust / MACD / Momentum）**

`oil_price_daily_ohlcv` 表有 **5386 条 LCO1 数据**（2006～2026），四个基础策略完全可以运行：

```json
{"symbol": "LCO1", "combineModes": ["baseOnly"]}
```

### ❌ 当前无法产生有效信号

**AND / VETO / ModelOnly 策略**

`prediction_run` 表现有 7 条记录，**全部是针对 2026-03-28 及以后的未来预测**，与 OHLCV 历史数据（截至 2026-02-20）没有任何重叠。因此这三种模式的交易信号全为 0，等效空仓，结果无意义。

根本原因：`prediction_run` 表设计用于存储每次实时调用 `/api/predict` 的结果，不是逐日滚动的历史回测预测序列。

### 解锁 ML 策略的方法

**推荐：通过导入接口一次性写入**

如果手头有 `gbo_tft_test_predictions_*.csv` 或 `ensemble.csv`，在本机运行以下脚本即可：

```python
import pandas as pd, requests

df = pd.read_csv("gbo_tft_test_predictions_cl0_1d_close_smooth.csv")
df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

payload = {
    "target": "BRENT",   # LCO1 对应 BRENT
    "horizon": "1d",
    "predictions": df[["date", "y_pred"]].rename(columns={"y_pred": "value"}).to_dict("records")
}

r = requests.post("http://localhost:8080/api/backtest/import-predictions", json=payload)
print(r.json())  # {"inserted": N, "skipped": 0, "total": N}
```

导入成功后，AND/VETO/ModelOnly 策略立即可用，无需重启服务。

**备选：积累实时预测**

每天调用一次 `POST /api/predict`（`horizon=1d`），随时间积累，回测覆盖范围逐步增大，但短期内覆盖区间太短，回测参考价值有限。

### 功能可用性总结

| 功能 | 状态 | 备注 |
|------|------|------|
| `GET /api/backtest/symbols` | ✅ 可用 | 返回 LCO1，2006-01-03 ~ 2026-02-20 |
| `GET /api/backtest` | ✅ 可用 | 使用说明 |
| baseOnly 策略（4 种） | ✅ 可用 | 5386 条 LCO1 数据，信号充足 |
| 成本敏感性分析 | ✅ 可用 | 与主回测同步输出 |
| 样本外（OOS）指标 | ✅ 可用 | 取后 20% 数据 |
| AND / VETO / ModelOnly | ❌ 暂无信号 | 需先导入历史预测数据 |
| `POST /api/backtest/import-predictions` | ✅ 可用 | 导入后 ML 策略立即解锁 |

---

## 八、与 Python 脚本的差异

| 特性 | Python 脚本 | Java 实现 |
|------|------------|----------|
| 数据来源 | CSV 文件（本地路径） | MySQL 数据库 |
| 预测来源 | CSV 文件（ensemble.csv 等） | `prediction_run` 表（需提前导入） |
| 输出形式 | CSV + PNG 图表 | REST API JSON |
| 图表绘制 | 生成 equity_curves.png | 返回 equityCurve 数组，由前端绘制 |
| EMA 实现 | pandas EWM adjust=False | 等价 Java 实现，数值结果一致 |
| 滚动标准差 | ddof=0 | 同 ddof=0 |
| OOS 分割 | 后 20% | 同后 20% |
| 成本敏感性 | 1×/2×/3× 费率 | 同 1×/2×/3× 费率 |
| forecastJson 格式 | 不涉及 | 兼容格式 A（point[].t/.v）和格式 B（predictions[].date/.value） |
