---
name: volume_price_momentum_analysis
description: 基于OBV、A/D Line、VWAP、CMF四大量价指标，判断标的资金流动方向、主力吸筹/派发状态、价格与量能配合度，适用于中短期趋势确认与反转预警。
owner_group: 专家组-技术分析
domain: technical
status: draft
---

# 量价动量综合分析

## 1. 适用范围

所属小组：专家组-技术分析

适用任务：
- 判断标的当前资金流入/流出方向与强度
- 识别主力吸筹、派发或洗盘行为
- 确认价格趋势的量能支撑是否健康
- 预警量价背离导致的趋势反转风险
- 辅助确定中短期入场/离场时机

适用对象：个股、行业ETF、宽基指数

适用时间周期：日线级别为主，可适配60分钟线做日内参考

边界说明：
- 单一指标信号不可直接作为交易决策，需至少2个指标共振确认
- 小盘股（流通市值<50亿）或庄股需人工复核，指标易被操纵
- 重大消息日、停牌复牌首日指标失真，标记人工复核
- 指标仅反映历史量价关系，不预测突发事件

## 2. 输入材料

### 必填输入

- 标的：股票代码 / 指数代码
- 时间范围：最近N个交易日（建议N≥60，覆盖至少3个月）
- 核心数据材料：
  - 日K线数据：开盘价、最高价、最低价、收盘价、成交量
  - 日内分时数据（VWAP计算必需）：分钟级OHLCV
- 数据来源：行情数据源（如wind、tushare、聚宽等）

### 可选输入

- 行业/板块同期量价数据（用于相对强度对比）
- 主力资金流向数据（验证指标信号）
- 历史同期量价特征（季节性参考）
- 人工标注的关键价位（支撑/阻力位）

### 缺失处理

- 如果日K线数据缺失超过连续5个交易日，输出 `direction: "neutral"`，`confidence` 降至0.3以下，在 `meta.uncertainties` 写明数据缺口，并设 `meta.needs_human_review: true`
- 如果缺少分钟级数据无法计算VWAP，跳过VWAP相关分析，在 `meta.uncertainties` 说明
- 如果成交量数据为0（停牌），标记该日期为无效数据，不参与计算

## 3. 分析步骤

按下面步骤分析：

1. **数据准备**：获取标的最近N日OHLCV数据，检查数据完整性
2. **指标计算**：
   - 计算OBV序列
   - 计算A/D Line序列
   - 计算日内VWAP（如有分钟数据）或滚动N日VWAP
   - 计算CMF（默认20日周期）
3. **极值检测**：识别价格和各指标的局部高点/低点（默认5日窗口确认）
4. **背离扫描**：逐对检查价格与OBV、A/D Line、CMF的顶背离/底背离
5. **趋势强度判定**：计算各指标N日斜率，与价格斜率对比
6. **VWAP位置判定**：当前价格相对VWAP的位置及穿越历史
7. **信号综合**：按权重汇总各子信号，生成最终direction和confidence
8. **证据整理**：记录关键数值、对比结论、数据来源
9. **不确定性标注**：写明数据缺口、指标冲突、需复核点
10. **输出标准JSON**

## 4. 判断规则

### 4.1 OBV（能量潮）判断规则

#### 规则OBV-1：OBV趋势确认
- **指标**：OBV 20日斜率
- **阈值**：斜率 > 0 为上升，斜率 < 0 为下降
- **时间窗口**：20日
- **判定**：
  - OBV斜率 > 0 且价格20日斜率 > 0：`direction` 偏 `bullish`，`confidence` +0.1
  - OBV斜率 < 0 且价格20日斜率 < 0：`direction` 偏 `bearish`，`confidence` +0.1
  - OBV斜率与价格斜率方向相反：`direction` 偏 `neutral`，触发背离检查

#### 规则OBV-2：OBV顶背离
- **指标**：价格局部高点 vs OBV局部高点
- **阈值**：价格新高（当前高点 > 前高点 × 1.02），OBV未新高（当前OBV高点 ≤ 前OBV高点 × 1.01）
- **时间窗口**：回溯60日，极值确认窗口5日
- **判定**：
  - `direction`: `bearish`
  - `confidence`: 0.65-0.85（单指标）；若同时A/D Line或CMF也背离，提升至0.80-0.95
  - `risk_level`: `medium`；若出现在长期上涨后，`high`
  - `signals`: 追加"OBV顶背离：上涨动能衰竭"

#### 规则OBV-3：OBV底背离
- **指标**：价格局部低点 vs OBV局部低点
- **阈值**：价格新低（当前低点 < 前低点 × 0.98），OBV未新低（当前OBV低点 ≥ 前OBV低点 × 0.99）
- **时间窗口**：回溯60日，极值确认窗口5日
- **判定**：
  - `direction`: `bullish`
  - `confidence`: 0.60-0.80（单指标）；多指标共振提升至0.75-0.90
  - `risk_level`: `medium`
  - `signals`: 追加"OBV底背离：抛压衰竭，潜在见底"

#### 规则OBV-4：OBV突破
- **指标**：OBV创60日新高/新低
- **阈值**：当前OBV > 60日OBV最大值 × 0.995（突破）或 < 60日OBV最小值 × 1.005（跌破）
- **判定**：
  - 突破且价格同步突破：`direction` 强化为 `bullish`，`confidence` +0.15
  - 跌破且价格同步跌破：`direction` 强化为 `bearish`，`confidence` +0.15
  - 单独突破但价格未跟进：`direction` `neutral`，标记"OBV领先，待价格确认"

---

### 4.2 A/D Line（累积/派发线）判断规则

#### 规则AD-1：A/D趋势方向
- **指标**：A/D Line 20日斜率
- **阈值**：斜率 > 0 为累积，斜率 < 0 为派发
- **时间窗口**：20日
- **判定**：
  - A/D斜率 > 0 且价格斜率 > 0：健康上涨，`direction` `bullish`，`confidence` +0.1
  - A/D斜率 < 0 且价格斜率 < 0：健康下跌，`direction` `bearish`，`confidence` +0.1
  - A/D斜率 > 0 但价格横盘或微跌：主力吸筹，`direction` 偏 `bullish`，`confidence` 0.55-0.70
  - A/D斜率 < 0 但价格横盘或微涨：主力派发，`direction` 偏 `bearish`，`confidence` 0.55-0.70

#### 规则AD-2：A/D顶背离
- **指标**：价格局部高点 vs A/D Line局部高点
- **阈值**：价格新高（>前高点×1.02），A/D未新高（≤前高点×1.01）
- **时间窗口**：回溯60日，极值确认窗口5日
- **判定**：
  - `direction`: `bearish`
  - `confidence`: 0.70-0.90（A/D对主力行为更敏感，置信度略高于OBV）
  - `risk_level`: `high`（派发信号通常更可靠）
  - `signals`: 追加"A/D顶背离：主力高位派发"

#### 规则AD-3：A/D底背离
- **指标**：价格局部低点 vs A/D Line局部低点
- **阈值**：价格新低（<前低点×0.98），A/D未新低（≥前低点×0.99）
- **时间窗口**：回溯60日，极值确认窗口5日
- **判定**：
  - `direction`: `bullish`
  - `confidence`: 0.65-0.85
  - `risk_level`: `medium`
  - `signals`: 追加"A/D底背离：主力低位吸筹"

#### 规则AD-4：A/D与价格强度比
- **指标**：A/D Line 20日变化率 / 价格20日变化率
- **阈值**：
  - 比值 > 1.5：A/D强于价格，资金积极流入
  - 比值 < 0.5：A/D弱于价格，资金跟进不足
- **判定**：
  - 比值 > 1.5 且价格上涨：`direction` `bullish`，`confidence` +0.1
  - 比值 < 0.5 且价格上涨：`direction` `neutral` 偏 `bearish`，`confidence` 0.50-0.65
  - 比值 > 1.5 且价格下跌：`direction` `neutral` 偏 `bullish`（吸筹迹象），`confidence` 0.50-0.65

---

### 4.3 VWAP（成交量加权平均价格）判断规则

#### 规则VWAP-1：VWAP位置判定
- **指标**：当前收盘价 vs 当日/滚动N日VWAP
- **阈值**：偏移幅度 = (收盘价 - VWAP) / VWAP
- **判定**：
  - 偏移 > +2% 且持续3日以上：`direction` `bullish`，`confidence` +0.1，`signals`: "站稳VWAP上方，多头主导"
  - 偏移 < -2% 且持续3日以上：`direction` `bearish`，`confidence` +0.1，`signals`: "跌破VWAP下方，空头主导"
  - 偏移在 ±1% 内：`direction` `neutral`，`signals`: "围绕VWAP震荡，方向不明"

#### 规则VWAP-2：VWAP穿越信号
- **指标**：价格上穿/下穿VWAP
- **阈值**：前一日收盘价 < VWAP 且当日收盘价 > VWAP（上穿）；反之亦然
- **判定**：
  - 上穿 + 成交量放大（当日成交量 > 20日均量 × 1.2）：`direction` `bullish`，`confidence` 0.60-0.75，`signals`: "放量突破VWAP，趋势转多"
  - 下穿 + 成交量放大：`direction` `bearish`，`confidence` 0.60-0.75，`signals`: "放量跌破VWAP，趋势转空"
  - 无量穿越：`direction` `neutral`，`confidence` 0.40-0.50，`signals`: "VWAP穿越但量能不足，待确认"

#### 规则VWAP-3：VWAP支撑/阻力测试
- **指标**：价格触碰VWAP次数及后续走势
- **阈值**：最近10个交易日内触碰VWAP ≥ 3次
- **判定**：
  - 触碰后反弹（收盘价 > VWAP）：`direction` 偏 `bullish`，`confidence` 0.55-0.70，`signals`: "VWAP支撑有效"
  - 触碰后跌破（收盘价 < VWAP）：`direction` 偏 `bearish`，`confidence` 0.55-0.70，`signals`: "VWAP阻力有效/支撑失效"

#### 规则VWAP-4：VWAP与长期成本偏离
- **指标**：当前价格 vs 20日VWAP vs 60日VWAP
- **阈值**：
  - 价格 > 20日VWAP > 60日VWAP：多头排列
  - 价格 < 20日VWAP < 60日VWAP：空头排列
- **判定**：
  - 多头排列：`direction` `bullish`，`confidence` +0.15
  - 空头排列：`direction` `bearish`，`confidence` +0.15

---

### 4.4 CMF（钱流量指标）判断规则

#### 规则CMF-1：CMF零轴穿越
- **指标**：CMF（20日）值及穿越方向
- **阈值**：CMF = 0 为零轴
- **判定**：
  - CMF 上穿零轴（前日 < 0 且当日 > 0）：`direction` `bullish`，`confidence` 0.55-0.70，`signals`: "CMF上穿零轴，资金由流出转流入"
  - CMF 下穿零轴（前日 > 0 且当日 < 0）：`direction` `bearish`，`confidence` 0.55-0.70，`signals`: "CMF下穿零轴，资金由流入转流出"
  - CMF 在零轴附近（±0.05）：`direction` `neutral`，`signals`: "CMF中性，资金平衡"

#### 规则CMF-2：CMF强度区间
- **指标**：CMF绝对值大小
- **阈值**：
  - CMF > +0.25：强势流入
  - CMF 在 +0.05 ~ +0.25：温和流入
  - CMF 在 -0.05 ~ +0.05：中性
  - CMF 在 -0.25 ~ -0.05：温和流出
  - CMF < -0.25：强势流出
- **判定**：
  - 强势流入 + 价格上涨：`direction` `bullish`，`confidence` 0.70-0.85，`risk_level`: `low`
  - 强势流出 + 价格下跌：`direction` `bearish`，`confidence` 0.70-0.85，`risk_level`: `low`
  - 强势流入 + 价格横盘：`direction` 偏 `bullish`，`confidence` 0.55-0.70，`signals`: "资金暗流吸筹"
  - 强势流出 + 价格横盘：`direction` 偏 `bearish`，`confidence` 0.55-0.70，`signals`: "资金暗流派发"

#### 规则CMF-3：CMF背离
- **指标**：价格局部高点/低点 vs CMF局部高点/低点
- **阈值**：同OBV/AD背离阈值
- **时间窗口**：回溯60日，极值确认窗口5日
- **判定**：
  - 顶背离：`direction` `bearish`，`confidence` 0.65-0.85
  - 底背离：`direction` `bullish`，`confidence` 0.60-0.80

#### 规则CMF-4：CMF趋势持续性
- **指标**：CMF连续处于同一区间天数
- **阈值**：连续 > 10日
- **判定**：
  - 连续 > 10日处于流入区间（>0）：`direction` 强化 `bullish`，`confidence` +0.1
  - 连续 > 10日处于流出区间（<0）：`direction` 强化 `bearish`，`confidence` +0.1

---

### 4.5 多指标共振与冲突处理

#### 规则COMBINE-1：多指标共振
- **条件**：至少3个指标给出同向信号
- **判定**：
  - 3-4个指标 `bullish`：`direction` `bullish`，`confidence` = max(单个confidence) + 0.1，上限0.95
  - 3-4个指标 `bearish`：`direction` `bearish`，`confidence` = max(单个confidence) + 0.1，上限0.95

#### 规则COMBINE-2：指标冲突
- **条件**：指标方向不一致（如OBV看多、CMF看空）
- **判定**：
  - `direction`: `neutral`
  - `confidence`: 0.40-0.55
  - `signals`: 追加"指标信号冲突，方向不明"
  - `meta.uncertainties`: 写明各指标方向及矛盾点
  - `meta.needs_human_review`: `true`

#### 规则COMBINE-3：单一指标极端信号
- **条件**：某一指标出现极端值（如CMF > +0.5 或 < -0.5，或VWAP偏离 > 5%）
- **判定**：
  - 标记为"极端值预警"
  - 不直接改变 `direction`，但提升 `risk_level` 至 `high`
  - `meta.needs_human_review`: `true`

#### 规则COMBINE-4：时间周期加权
- **短期信号**（VWAP日内/5日、CMF 5日）：权重 0.3
- **中期信号**（OBV 20日、A/D 20日、CMF 20日）：权重 0.5
- **长期信号**（OBV 60日、A/D 60日、VWAP 60日）：权重 0.2
- **综合得分** = Σ(信号方向 × 权重)，方向取+1(bullish)/-1(bearish)/0(neutral)
- **最终direction**：
  - 得分 > +0.3：`bullish`
  - 得分 < -0.3：`bearish`
  - 否则：`neutral`

## 5. 标准输出

最终输出JSON：

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
    "owner_group": "专家组-技术分析",
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
    "needs_human_review": true,
    "sub_signals": {
      "obv": {
        "signal": "",
        "direction": "",
        "confidence": 0.0,
        "latest_value": 0.0,
        "slope_20d": 0.0
      },
      "ad_line": {
        "signal": "",
        "direction": "",
        "confidence": 0.0,
        "latest_value": 0.0,
        "slope_20d": 0.0
      },
      "vwap": {
        "signal": "",
        "direction": "",
        "confidence": 0.0,
        "latest_value": 0.0,
        "price_deviation_pct": 0.0
      },
      "cmf": {
        "signal": "",
        "direction": "",
        "confidence": 0.0,
        "latest_value": 0.0,
        "zone": ""
      }
    },
    "divergence_detected": {
      "bearish_divergence": false,
      "bullish_divergence": false,
      "involved_indicators": [],
      "divergence_span_days": 0
    }
  }
}
```

### meta.sub_signals 说明

`meta.sub_signals` 记录四个指标的独立判断结果，便于开发2组做信号追溯和仲裁：

- `obv.signal`：OBV子信号描述，如"OBV顶背离"、"OBV趋势上升"
- `obv.direction`：OBV独立判断方向
- `obv.confidence`：OBV独立置信度
- `obv.latest_value`：最新OBV值
- `obv.slope_20d`：OBV 20日斜率

其他三个指标字段含义相同。

### meta.divergence_detected 说明

- `bearish_divergence`：是否检测到顶背离
- `bullish_divergence`：是否检测到底背离
- `involved_indicators`：参与背离的指标列表，如["OBV", "CMF"]
- `divergence_span_days`：背离跨度（两个极值点之间的交易日数）

## 6. 质量检查

输出前检查：

- [ ] `direction` 是否明确（bullish/bearish/neutral）
- [ ] `confidence` 是否在 0.0-1.0 范围内
- [ ] `signal_type` 是否为 "technical"
- [ ] `signals` 是否至少包含一条核心信号
- [ ] `meta.sub_signals` 是否四个指标都有记录
- [ ] `meta.evidence` 是否至少包含价格、成交量、各指标最新值
- [ ] `meta.time_horizon` 是否根据信号类型正确标注（VWAP日内信号标short，OBV/AD中期标mid）
- [ ] `meta.risk_level` 是否与背离、极端值、指标冲突匹配
- [ ] `meta.uncertainties` 是否写明数据缺口或指标冲突
- [ ] `meta.needs_human_review` 是否在以下情况设为true：
  - 数据缺失超过连续5日
  - 指标信号严重冲突（2个看多2个看空）
  - 检测到极端值（CMF>0.5或<-0.5，VWAP偏离>5%）
  - 小盘股（流通市值<50亿）
  - 重大消息日或停牌复牌首日
