---
name: volume_price_momentum_analysis
description: 基于 OBV、A/D Line、VWAP、CMF 四大量价指标，判断标的资金流动方向、主力吸筹/派发状态、价格与量能配合度，适用于中短期趋势确认与反转预警。
owner_group: 专家2组（指标）
domain: technical
status: draft
---

# 量价动量综合分析

## 1. 适用范围

所属小组：专家2组（指标）

适用任务：
- 判断个股、行业 ETF、宽基指数当前资金流入/流出方向与强度。
- 识别主力吸筹、派发、洗盘或量价背离风险。
- 确认价格趋势是否获得成交量和资金流指标支撑。
- 辅助中短期趋势确认、反转预警和入场/离场时机判断。

边界说明：
- 单一指标信号不可直接作为交易决策，至少需要 2 个指标共振确认。
- 小盘股、庄股、重大消息日、停牌复牌首日的量价指标容易失真，需要人工复核。
- 缺少分钟级数据时，可以使用滚动区间 VWAP 近似，但必须在 `meta.uncertainties` 中说明。
- 本 Skill 只反映历史量价关系，不预测突发事件，也不直接生成交易指令。

## 2. 输入材料

### 必填输入

- 标的：股票代码 / 指数代码 / ETF 代码。
- 时间范围：最近 N 个交易日，建议 N >= 60，覆盖至少 3 个月。
- 核心数据材料：日 K 线 OHLCV，包括开盘价、最高价、最低价、收盘价、成交量。
- 数据来源：行情数据源、人工上传 CSV、Wind、Tushare、聚宽或其他可信行情源。

### 可选输入

- 分钟级 OHLCV，用于更精确计算日内 VWAP。
- 行业或指数同期量价数据，用于相对强度对比。
- 主力资金流向、北向资金、龙虎榜等资金数据，用于验证量价信号。
- 人工标注的关键支撑位、阻力位、重大事件日期。

### 缺失处理

- 如果日 K 线必填字段缺失，输出 `direction: "neutral"`，`confidence` 降至 0.4 以下，在 `meta.uncertainties` 写明缺失字段，并把 `meta.needs_human_review` 设为 `true`。
- 如果日 K 线数据连续缺失超过 5 个交易日，输出 `direction: "neutral"`，`confidence` 降至 0.3 以下，在 `meta.uncertainties` 写明数据缺口，并把 `meta.needs_human_review` 设为 `true`。
- 如果缺少分钟级数据，则使用日线典型价滚动 VWAP 或区间累积 VWAP 近似，并在 `meta.uncertainties` 中说明。
- 如果成交量为 0，应将该交易日标记为无效数据；若无效数据影响最近 20 个交易日判断，降低 `confidence` 并标记人工复核。

## 3. 分析步骤

按下面步骤分析：

1. 明确分析对象、时间范围、数据来源和复权口径。
2. 检查 OHLCV 字段完整性、有效交易日数量、成交量异常和连续缺口。
3. 计算 OBV、A/D Line、CMF(20)、VWAP 或滚动 VWAP。
4. 识别价格和指标的局部高点/低点，默认使用 5 日确认窗口和 60 日回溯窗口。
5. 扫描价格与 OBV、A/D Line、CMF 的顶背离和底背离。
6. 计算价格、OBV、A/D Line 的 20 日斜率，并判断趋势方向是否一致。
7. 判断当前价格相对 VWAP 的位置、偏离幅度、穿越状态和成本排列。
8. 按多指标共振、冲突、极端值规则汇总 `direction`、`confidence`、`risk_level`。
9. 整理 `signals`、`reasoning`、`meta.key_findings`、`meta.evidence`、`meta.risk_notes` 和 `meta.uncertainties`。
10. 输出与当前项目 `agents.signal.Signal` 对齐的标准 JSON。

## 4. 判断规则

### 4.1 OBV（能量潮）

规则 OBV-1：趋势确认
- 指标：OBV 20 日线性斜率与价格 20 日斜率。
- 阈值：斜率 > 0 为上升，斜率 < 0 为下降。
- 判定：OBV 与价格同向上升，偏 `bullish`，`confidence` 增加 0.10；同向下降，偏 `bearish`，`confidence` 增加 0.10；方向相反时触发背离检查并降低置信度。
- evidence：记录最新 OBV、20 日斜率、价格 20 日变化。

规则 OBV-2：顶背离
- 指标：价格局部高点 vs OBV 局部高点。
- 阈值：价格新高为当前高点 > 前高点 x 1.02；OBV 未新高为当前 OBV 高点 <= 前 OBV 高点 x 1.01。
- 时间窗口：回溯 60 日，极值确认窗口 5 日。
- 判定：`direction` 偏 `bearish`，单指标 `confidence` 0.65-0.85；若 A/D Line 或 CMF 同时背离，提升至 0.80-0.95，`risk_level` 至少 `medium`。
- signals：追加“OBV 顶背离：上涨动能衰竭”。

规则 OBV-3：底背离
- 指标：价格局部低点 vs OBV 局部低点。
- 阈值：价格新低为当前低点 < 前低点 x 0.98；OBV 未新低为当前 OBV 低点 >= 前 OBV 低点 x 0.99。
- 时间窗口：回溯 60 日，极值确认窗口 5 日。
- 判定：`direction` 偏 `bullish`，单指标 `confidence` 0.60-0.80；多指标共振时提升至 0.75-0.90，`risk_level` 至少 `medium`。
- signals：追加“OBV 底背离：抛压衰竭，潜在见底”。

规则 OBV-4：突破确认
- 指标：OBV 是否创 60 日新高/新低，价格是否同步突破/跌破。
- 阈值：当前 OBV > 60 日 OBV 最大值 x 0.995 视为突破；当前 OBV < 60 日 OBV 最小值 x 1.005 视为跌破。
- 判定：OBV 与价格同步突破强化 `bullish`，同步跌破强化 `bearish`；若仅 OBV 领先而价格未跟进，则保持 `neutral`，并写入 `meta.uncertainties`。

### 4.2 A/D Line（累积/派发线）

规则 AD-1：趋势方向
- 指标：A/D Line 20 日斜率与价格 20 日斜率。
- 判定：A/D 与价格同向上升，偏 `bullish`；同向下降，偏 `bearish`；A/D 上升但价格横盘或微跌，视为低位吸筹，偏 `bullish`，`confidence` 0.55-0.70；A/D 下降但价格横盘或微涨，视为派发，偏 `bearish`，`confidence` 0.55-0.70。

规则 AD-2：顶背离
- 指标：价格局部高点 vs A/D Line 局部高点。
- 阈值：价格新高 > 前高点 x 1.02，A/D 未新高 <= 前高点对应 A/D 值 x 1.01。
- 时间窗口：回溯 60 日，极值确认窗口 5 日。
- 判定：`direction` 偏 `bearish`，`confidence` 0.70-0.90，`risk_level` 至少 `high`。
- signals：追加“A/D 顶背离：主力高位派发”。

规则 AD-3：底背离
- 指标：价格局部低点 vs A/D Line 局部低点。
- 阈值：价格新低 < 前低点 x 0.98，A/D 未新低 >= 前低点对应 A/D 值 x 0.99。
- 时间窗口：回溯 60 日，极值确认窗口 5 日。
- 判定：`direction` 偏 `bullish`，`confidence` 0.65-0.85，`risk_level` 至少 `medium`。
- signals：追加“A/D 底背离：主力低位吸筹”。

规则 AD-4：A/D 与价格强度比
- 指标：A/D Line 20 日变化率 / 价格 20 日变化率。
- 阈值：比值 > 1.5 表示 A/D 强于价格，资金积极流入；比值 < 0.5 表示 A/D 弱于价格，资金跟进不足。
- 判定：价格上涨且比值 > 1.5 偏 `bullish`；价格上涨但比值 < 0.5 偏 `neutral` 或 `bearish`；价格下跌但比值 > 1.5 偏 `neutral` 或 `bullish`，并提示吸筹迹象。

### 4.3 VWAP（成交量加权平均价格）

规则 VWAP-1：位置判定
- 指标：当前收盘价 vs 当日/滚动 VWAP。
- 阈值：偏移幅度 = (收盘价 - VWAP) / VWAP。
- 判定：偏移 > +2% 且持续 3 日以上，偏 `bullish`；偏移 < -2% 且持续 3 日以上，偏 `bearish`；偏移在 +/-1% 内，偏 `neutral`。
- evidence：记录最新收盘价、VWAP、偏离百分比。

规则 VWAP-2：穿越信号
- 指标：价格上穿/下穿 VWAP。
- 阈值：前一日收盘价 < VWAP 且当日收盘价 > VWAP 为上穿；反之为下穿；成交量放大为当日成交量 > 20 日均量 x 1.2。
- 判定：放量上穿偏 `bullish`，`confidence` 0.60-0.75；放量下穿偏 `bearish`，`confidence` 0.60-0.75；无量穿越保持 `neutral`，`confidence` 0.40-0.50。

规则 VWAP-3：支撑/阻力测试
- 指标：最近 10 个交易日触碰 VWAP 次数及后续走势。
- 阈值：触碰 VWAP >= 3 次。
- 判定：触碰后反弹并收于 VWAP 上方，偏 `bullish`；触碰后跌破并收于 VWAP 下方，偏 `bearish`。

规则 VWAP-4：成本排列
- 指标：当前价格、20 日 VWAP、60 日 VWAP。
- 阈值：价格 > 20 日 VWAP > 60 日 VWAP 为多头排列；价格 < 20 日 VWAP < 60 日 VWAP 为空头排列。
- 判定：多头排列强化 `bullish`，空头排列强化 `bearish`，`confidence` 增加 0.15。

### 4.4 CMF（钱流量指标）

规则 CMF-1：零轴穿越
- 指标：CMF(20) 值及穿越方向。
- 阈值：CMF = 0 为零轴；+/-0.05 以内视为中性区。
- 判定：上穿零轴偏 `bullish`，下穿零轴偏 `bearish`；零轴附近为 `neutral`。

规则 CMF-2：强度区间
- 指标：CMF(20) 最新值。
- 阈值：CMF > +0.25 为强势流入；+0.05 到 +0.25 为温和流入；-0.05 到 +0.05 为中性；-0.25 到 -0.05 为温和流出；< -0.25 为强势流出。
- 判定：强势流入且价格上涨，偏 `bullish`，`confidence` 0.70-0.85；强势流出且价格下跌，偏 `bearish`，`confidence` 0.70-0.85；强势流入但价格横盘，提示吸筹；强势流出但价格横盘，提示派发。

规则 CMF-3：CMF 背离
- 指标：价格局部高点/低点 vs CMF 局部高点/低点。
- 阈值：同 OBV 背离阈值。
- 时间窗口：回溯 60 日，极值确认窗口 5 日。
- 判定：顶背离偏 `bearish`，`confidence` 0.65-0.85；底背离偏 `bullish`，`confidence` 0.60-0.80。

规则 CMF-4：持续性
- 指标：CMF 连续处于流入或流出区间的天数。
- 阈值：连续 > 10 日。
- 判定：连续流入强化 `bullish`，连续流出强化 `bearish`，`confidence` 增加 0.10。

### 4.5 多指标共振与冲突

规则 COMBINE-1：多指标共振
- 条件：至少 3 个指标给出同向信号。
- 判定：3-4 个指标同为 `bullish`，最终 `direction` 为 `bullish`；3-4 个指标同为 `bearish`，最终 `direction` 为 `bearish`；`confidence` = max(单指标置信度) + 0.10，上限 0.95。

规则 COMBINE-2：指标冲突
- 条件：指标方向明显不一致，例如 2 个看多、2 个看空，或 OBV 与 A/D Line 方向相反且斜率均显著。
- 判定：最终 `direction` 为 `neutral`，`confidence` 0.40-0.55；`signals` 追加“指标信号冲突，方向不明”；`meta.uncertainties` 写明各指标方向和矛盾点；`meta.needs_human_review` 设为 `true`。

规则 COMBINE-3：极端值预警
- 条件：CMF > +0.50 或 < -0.50，或 VWAP 偏离 > 5%，或成交量突然放大至 20 日均量 3 倍以上。
- 判定：不单独改变 `direction`，但将 `risk_level` 提升至 `high`，写入 `meta.risk_notes`，并把 `meta.needs_human_review` 设为 `true`。

规则 COMBINE-4：时间周期加权
- 短期信号：VWAP 日内/5 日、CMF 5 日，权重 0.30。
- 中期信号：OBV 20 日、A/D Line 20 日、CMF 20 日，权重 0.50。
- 长期信号：OBV 60 日、A/D Line 60 日、VWAP 60 日，权重 0.20。
- 综合得分 = sum(信号方向 x 权重)，其中 `bullish` 为 +1，`bearish` 为 -1，`neutral` 为 0。
- 最终方向：得分 > +0.30 为 `bullish`；得分 < -0.30 为 `bearish`；否则为 `neutral`。

### 4.6 证据、周期和风险字段规则

- `meta.evidence` 至少记录价格、成交量、OBV、A/D Line、CMF、VWAP 中的核心证据，`source_type` 使用 `market_data`；如有主力资金数据，使用 `fund_flow`。
- `meta.time_horizon` 根据信号来源确定：VWAP 穿越和短期 CMF 信号为 `short`；OBV/A-D/CMF 20 日趋势为 `mid`；60 日背离和成本排列为 `mid` 或 `long`。
- `meta.risk_level` 默认为 `low`；出现单指标背离、指标冲突或数据缺口时为 `medium`；出现多指标背离、极端值、重大缺口或复牌首日时为 `high`。
- `meta.key_findings` 提炼 1-5 条最重要的量价结论，必须能被 `meta.evidence` 支撑。
- `meta.risk_notes` 记录背离、极端偏离、成交量异常、数据口径问题等风险提示。
- `meta.uncertainties` 记录缺失数据、口径不明、分钟级 VWAP 缺失、指标冲突等不确定性。
- `meta.needs_human_review` 在数据缺失、指标严重冲突、极端值、小盘股、重大消息日、停牌复牌首日或证据来源可信度不足时设为 `true`。
- 专业追溯字段可以放在 `meta.sub_signals` 和 `meta.divergence_detected`，但不得改变标准顶层字段。

## 5. 标准输出

最终输出 JSON，顶层字段与当前项目 `agents.signal.Signal` 对齐。证据、风险等级、时间周期、关键发现、不确定性和人工复核点统一放在 `meta` 中。

```json
{
  "direction": "bullish | bearish | neutral",
  "confidence": 0.0,
  "reasoning": "",
  "signals": [],
  "source": "volume_price_momentum_analysis",
  "signal_type": "technical",
  "stock_code": "",
  "weight": 1.0,
  "meta": {
    "output_version": "0.1",
    "skill_name": "volume_price_momentum_analysis",
    "owner_group": "专家2组（指标）",
    "target": "",
    "period": "",
    "time_horizon": "short | mid | long",
    "risk_level": "low | medium | high",
    "key_findings": [],
    "evidence": [
      {
        "source_type": "market_data",
        "source_name": "",
        "date": "",
        "metric": "",
        "value": "",
        "comparison": "",
        "note": ""
      }
    ],
    "risk_notes": [],
    "uncertainties": [],
    "needs_human_review": true
  }
}
```

说明：
- `direction` 只能是 `bullish`、`bearish`、`neutral`，不能新增 `risk_warning`。
- `confidence` 范围是 0.0 到 1.0，证据充分且多指标一致时可高于 0.80，证据不足或冲突时应低于 0.60。
- `signals` 写最核心的短句，便于调试和 UI 展示。
- `reasoning` 写简明推理摘要，详细证据放入 `meta.evidence`。
- `source` 固定为 `volume_price_momentum_analysis`。
- `signal_type` 固定为 `technical`。
- `weight` 第一阶段固定为 1.0，后续由仲裁层决定是否调整。

## 字段中英对照

| 字段 | 中文含义 | 填写说明 |
|---|---|---|
| `direction` | 方向 | `bullish` 看多；`bearish` 看空；`neutral` 中性 |
| `confidence` | 置信度 | 0.0 到 1.0，越高表示越确定 |
| `reasoning` | 推理摘要 | 简要说明为什么得出这个结论 |
| `signals` | 核心信号 | 放最重要的量价信号短句 |
| `source` | 信号来源 | 固定写 Skill 名 |
| `signal_type` | 信号类型 | 固定写 `technical` |
| `stock_code` | 股票代码 | 没有股票代码时可留空，并在 `meta.target` 写标的名称 |
| `weight` | 权重 | 第一阶段填 1.0 |
| `meta` | 证据包/上下文包 | 放证据、风险等级、周期、人工复核点等 |
| `time_horizon` | 时间周期 | `short` 短期；`mid` 中期；`long` 长期 |
| `risk_level` | 风险等级 | `low` 低；`medium` 中；`high` 高 |
| `evidence` | 证据 | 记录来源、日期、指标、数值和说明 |
| `uncertainties` | 不确定性 | 数据缺失、口径不一致、需要复核的地方 |
| `needs_human_review` | 是否需要人工复核 | `true` 是；`false` 否 |

## source_type 来源类型

本 Skill 优先使用以下 `source_type`：

| source_type | 中文含义 | 示例 |
|---|---|---|
| `market_data` | 行情数据 | 价格、成交量、OHLCV、技术指标 |
| `fund_flow` | 资金流数据 | 主力资金、北向资金、龙虎榜 |
| `industry_data` | 行业数据 | 行业指数、行业成交量、相对强度 |
| `news` | 新闻 | 重大消息日或事件冲击 |
| `expert_input` | 人工输入 | 人工标注支撑/阻力、复权口径、异常交易日 |

## 方向、置信度、风险等级怎么判断

### direction 方向映射

- 正面资金流入、趋势确认、量价同步改善：`bullish`。
- 资金流出、趋势破坏、顶背离、放量跌破成本线：`bearish`。
- 数据不足、信号冲突、围绕 VWAP 震荡或仅监控提示：`neutral`。

### confidence 置信度分档

- `0.80 - 1.00`：至少 3 个指标同向，且证据完整。
- `0.60 - 0.80`：2 个以上指标同向，但存在少量不确定性。
- `0.40 - 0.60`：证据有限、指标冲突或只有单一指标支持。
- `< 0.40`：必填输入不足或数据质量较差，通常使用 `neutral` 并标记人工复核。

### risk_level 风险等级分档

- `low`：量价配合正常，没有明显背离或数据问题。
- `medium`：出现单指标背离、指标冲突、短期成交量异常或轻微数据缺口。
- `high`：出现多指标背离、极端偏离、重大数据缺口、复牌首日或重大消息日。

### time_horizon 时间周期

- `short`：VWAP 穿越、短期 CMF 变化、事件日成交量异动。
- `mid`：OBV/A-D/CMF 20 日趋势、20 日 VWAP 偏离。
- `long`：60 日背离、长期成本排列、跨季度资金趋势。

## 6. 质量检查

输出前检查：

- 是否有明确 `direction`。
- `confidence` 是否在 0.0 到 1.0。
- 是否写明 `signal_type: "technical"`。
- 是否有至少一条核心 `signals`。
- 是否有证据来源，且 `meta.evidence` 至少 1 条。
- 是否标注 `meta.time_horizon` 与 `meta.risk_level`。
- 缺失数据、分钟级 VWAP 不可用、复权口径不明是否写入 `meta.uncertainties`。
- 是否根据风险和数据质量正确设置 `meta.needs_human_review`。
- `meta.key_findings` 是否能被 `meta.evidence` 支撑。
- 如果保留 `meta.sub_signals` 或 `meta.divergence_detected`，是否只作为追溯字段，不影响标准顶层字段。

