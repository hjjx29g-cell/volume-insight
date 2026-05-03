# 📊 量能综合分析报告 – {股票名称/代码}

> **与主仓契约**：AI Renaissance 流程中优先产出标准 **`Signal` JSON**（见 `SKILL.md` §5）。本 Markdown 为人类可读附录，可填入 `meta.report_markdown` 或单独存档。

**分析周期**：{start_date} 至 {end_date}（共 {n_days} 个交易日）

## 1️⃣ OBV – 资金方向
- 趋势：{obv_trend}
- 背离信号：{obv_divergence}
- 解读：{obv_interpretation}

## 2️⃣ A/D Line – 资金质量
- 趋势：{adl_trend}
- 背离信号：{adl_divergence}
- 与 OBV 一致性：{consistency}

## 3️⃣ CMF(20) – 资金强度
- 当前值：{cmf_value}
- 评级：{cmf_rating}
- 近期变化：{cmf_change}

## 4️⃣ VWAP – 成本基准
- 区间 VWAP：{vwap}
- 最新收盘价：{close}（{price_vs_vwap} VWAP）
- 含义：{vwap_meaning}

## 5️⃣ 综合结论与操作启示
- **综合评级**：{composite_rating}
- **关键逻辑**：{key_reasons}
- **操作建议**：
  - 做多条件：{long_conditions}
  - 做空/离场条件：{short_conditions}
  - 止损参考：{stop_loss}

## 6️⃣ 数据附录（最近5日）
| 日期 | OBV | A/D | CMF | VWAP |
|------|-----|-----|-----|------|
| ... | ... | ... | ... | ... |
