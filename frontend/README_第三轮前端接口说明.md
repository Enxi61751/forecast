# 第三轮前端迭代接口说明（临时占位版）

## 1. 说明目的

本说明用于给前端第三轮迭代做接口边界约定。

当前仓库以 **frontend 现有实现为主** 继续推进，本轮前端允许先完成页面结构、状态流转、适配器层和空态承接；对于尚未合并的 backend 接口，统一按 **占位 / 留空 / unavailable** 处理，不在前端擅自发明正式协议。

本说明的核心原则是：

1. **只做 front-end，不修改 backend。**
2. **当前分支先以现有 front-end 请求方式保持可运行。**
3. **未来 backend branch 合并后，只在 `src/api/*` 和 `src/api/adapters/*` 做对齐，不把接口兼容逻辑散落到页面组件。**
4. **页面层允许先展示 loading / empty / error / unavailable / success 状态。**

---

## 2. 当前前端接口基线

在当前 front-end 分支中，前端继续以现有请求体系为基线推进第三轮页面开发。

### 2.1 当前优先保留的前端调用口径

- 预测类页面当前以前端现有的 `predict` 请求封装为准。
- 即使审计中发现 backend 另一处证据显示控制器可能暴露为 `/api/predict/run`，本轮 **当前分支仍以 front-end 现有调用方式为主**，避免因为后端 branch 尚未合并而阻塞前端开发。
- 等后端 branch 合并后，再统一在 adapter / api 层做 endpoint 和 request body 对齐。

换句话说：

> **本轮先保证前端结构、页面、状态、组件拆分和交互逻辑收敛；接口最终对齐留到后端 branch 合并后，在 API 层做一次集中修正。**

---

## 3. 已确认可以继续沿用的接口能力

以下能力在当前审计基线下，可作为前端继续迭代的依据：

### 3.1 预测能力

前端已有预测页面、预测表单、预测摘要卡片、运行状态展示区，因此：

- “汇率预测页收敛为 next-day 单点预测”可以先做。
- “新增 WTI 原油 next-day 单点预测页”也可以先做。
- 如果后端接口字段未最终合并，前端先通过 adapter 兼容当前字段，缺失字段以空态显示。

### 3.2 报告/可解释性展示能力

前端已有 explainability / report 类页面和展示容器，因此：

- 原油预测页中的 explanation slot 可以先预留。
- 回测页中的 summary/report 区块也可以先预留。
- 若 backend 未返回实际数据，则显示 empty / unavailable 状态。

### 3.3 新闻/事件/行情类展示能力

前端已经存在 news/events/exchange 相关页面和 adapter 思路，因此：

- 可以继续复用现有页面骨架和 adapter 模式。
- 若 backend 当前 branch 中没有对应 controller，也不阻塞第三轮页面层开发。

---

## 4. 本轮明确“留空”的接口

下面这些接口或数据协议，在当前联调分支中 **视为未最终落定**。前端本轮只预留承接位，不认定它们已经正式可用。

## 4.1 Agent / 多智能体展示接口

前端页面先做了以下内容：

- agent 列表容器
- 单个 agent 卡片
- loading / empty / error / unavailable / success 五态
- adapter 层中的 TODO 类型映射

以下内容留空：

- 最终 endpoint 路径
- 最终返回字段名
- 是否直接返回 `agent_actions`
- 是否返回 `execution_report`
- 是否返回 `market_sim_report`
- 是否有统一的 daily report DTO
- 是否有 agent 执行顺序 / 权重 / 风险等级字段

---

## 4.2 Backtest / 策略回测接口

前端页面先做了以下内容：

- cumulative return 图表容器
- metric cards
- benchmark 对比位
- summary panel
- empty / unavailable 分支

但以下内容留空了：

- backtest endpoint 路径
- benchmark 字段名
- cumulative return 序列字段名
- drawdown 序列字段名
- Sharpe / win rate / volatility 等指标字段是否存在
- trade summary 的最终结构
- period summary 的最终结构

---

## 4.3 原油预测返回中的扩展字段

WTI 原油预测页除“next-day 单点预测结果”之外，以下扩展字段未最终确认：

- confidence
- risk label
- explanation text
- decomposition overlay
- report reference id

### 本轮处理方式

- 页面先保留这些展示位。
- adapter 中允许写 TODO 兼容。
- 若当前 branch 没有字段，则页面仅显示基础预测结果和空态占位。


## 4.4 Exchange / News / Events 的最终后端来源

前端已有相关页面和 adapter，但当前联调分支中，以下接口的 controller 证据并不完整：

- `/api/data/exchange`
- `/api/data/events`
- `/api/news/list`

### 本轮处理方式

- 前端继续保留现有页面和 adapter 设计。
- 若当前分支未真正联通后端，则以 mock / empty / unavailable 承接。
- 等 backend branch 合并后再统一核对 endpoint。

---

## 5. 对 `/api/predict` 与 `/api/predict/run` 冲突的说明


### 现状

- front-end 当前实现使用的是：`/api/predict`
- 审计中发现 backend 的另一份证据中可能暴露的是：`/api/predict/run`

### 本轮约定

由于后端相关改动还在其他 branch，当前不方便合并，因此本轮前端采用以下处理原则：

1. **当前开发分支先保持 front-end 现有调用方式，优先保证页面开发不断。**
2. **不要在页面组件中直接写死 endpoint。**
3. **所有 endpoint 和 request body 的差异统一收敛到 `src/api/predict.ts` 和 `src/api/adapters/predictAdapter.ts`。**
4. **等 backend branch 合并后，再进行一次 API 层对齐。**


