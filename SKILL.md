---
name: volume_insight
description: 基于 OHLCV 对 OBV、A/D Line、CMF(20)、区间累积 VWAP 做四指标量能综合诊断；在用户提及量能、资金流向、OBV/A/D/CMF/VWAP 或「量能分析」类问题时启用。输出须对齐标准 Signal JSON，并可附 Markdown 报告草稿至 meta。
owner_group: 专家2组（指标）
domain: technical
status: draft
---

# Volume Insight — 四指标量能与资金流向综合 Skill（AI Renaissance v0.1 对齐）

本 Skill 将 **OBV（方向）**、**A/D Line（质量）**、**CMF（强度）**、**区间累积 VWAP（成本基准）** 结合，形成可仲裁的技术面 `Signal`。专业释义与公式见 `references/`；可复用计算见 `scripts/`。

**实现约定（避免与行情软件混淆）**：本仓库 `scripts/compute_vwap.py` 为 **日线序列上的区间累积 VWAP**（典型价 (H+L+C)/3，从样本起点逐根累积），**不是**「每个交易日重置的日内分时 VWAP」。证据与结论中应使用「区间 VWAP」表述。

---

## 1. 适用范围

**所属小组**：专家2组（指标）

**适用任务**：

- 单标的或给定 OHLCV 序列的量能结构、资金流向强弱、量价背离粗判。
- 需要把四指标压缩为 **bullish / bearish / neutral** 与置信度，供上层仲裁。

**适用对象**：股票、ETF、指数等具备可靠 OHLCV 的标的（流动性过差时降低 confidence）。

**适用周期**：以日线为主；最小样本见「输入材料」。若仅有周线，可运行但须在 `meta.uncertainties` 说明周期。

**边界说明**：

- 本 Skill **不替代**基本面、财报与消息面；结论为 **技术量能维度**，默认 `time_horizon` 偏 `short`～`mid`。
- **不构成投资建议**；`risk_level` 较高或 `needs_human_review` 为 true 时，禁止单独作为交易依据。
- 仅问纯价格指标（如单独 RSI/MACD）且明确不需要成交量时，**不要**启用本 Skill。

---

## 2. 输入材料

### 必填输入

| 项目 | 说明 |
|------|------|
| 标的 | 股票代码 / 名称 / 指数代码（无代码时写入 `meta.target` 文本） |
| 时间范围 | 分析区间起止日期；须能对应到 OHLCV 行 |
| 核心数据 | **OHLCV**：每行至少 `date, open, high, low, close, volume`（列名可映射，须在 `meta.uncertainties` 说明） |
| 数据来源 | `market_data`：行情终端、CSV 上传、开发3组数据接口等 |

### 可选输入

- 人工观点、截图、研报摘要
- 行业或基准指数 OHLCV（用于相对强弱时，在证据中单独列出）

### 缺失处理

- **缺少必填 OHLCV 任一字段、或可解析行数 &lt; 30**：输出 `direction: "neutral"`，`confidence` ≤ 0.35，在 `meta.uncertainties` 写明缺失项；`meta.needs_human_review: true`。
- **VWAP 无法计算**（例如有效成交量累加为 0）：该子项不计票；`uncertainties` 说明；若同时缺多项子指标，`needs_human_review: true`。
- **可选输入缺失**：可继续分析，在 `meta.uncertainties` 说明可能偏差。

---

## 3. 分析步骤

1. 确认标的、区间、数据来源；检查 OHLCV 列与单位（成交量是否复权一致须在证据或 uncertainties 中说明）。
2. 校验样本量：有效交易日 **≥ 30**；不足则按「缺失处理」降级输出。
3. 计算或调用脚本：`OBV`、`A/D Line`、`CMF(20)`、`区间累积 VWAP`（见 `scripts/`）；CMF 前若干根可能为 NaN，使用最后一根有效 CMF 或按脚本约定处理。
4. **背离（20 日窗口）**：比较价格与 OBV 的局部极值；记录是否存在顶/底背离（写入 `meta.evidence`）。
5. **A/D 与 OBV 一致性**：近 20 日 A/D 与 OBV 同向为一致，反向为矛盾（降低 `confidence`，写入 `uncertainties`）。
6. 按 **§4 判断规则** 汇总 `direction`、`confidence`、`risk_level`。
7. 组装 **§5 标准输出 JSON**；`meta.key_findings` 3～5 条短句；详细推理写入 `reasoning`。
8. **（可选）** 按 `assets/report-template.md` 生成 Markdown 报告草稿，全文可放入 `meta.report_markdown`（若主仓 `Signal` 暂未定义该字段，则作为联调扩展字段保留在 `meta` 中，或拆入 `key_findings`）。

---

## 4. 判断规则

以下规则用于 **每次** 分析产生 `direction`、`confidence`、`risk_level`。子指标数值应由数据计算，不得虚构。

### 4.1 计票（偏多票 / 偏空票）

在有效数据前提下，四行子规则各 **最多贡献 1 票**（共最多 4 票偏多、4 票偏空）。

**偏多票 +1 当：**

| 子规则 | 条件 |
|--------|------|
| OBV | 近 5 日 OBV 相对 5 日前为**上升**，**或**（20 日内**底背离**：价创新低而 OBV 未创新低）— 二者满足其一即可 +1，不重复计 |
| A/D | 近 20 日 A/D 序列整体**抬升**（末值高于期初足够幅度，或线性斜率 &gt; 0），且与 OBV **不矛盾**（见 4.1 末） |
| CMF | 最后一根有效 CMF(20) **&gt; 0.1** |
| VWAP | 收盘价 **&gt;** 区间累积 VWAP（序列最后一根） |

**偏空票 +1 当：**

| 子规则 | 条件 |
|--------|------|
| OBV | 近 5 日 OBV **下降**，**或**（20 日内**顶背离**：价创新高而 OBV 未创新高）— 满足其一 +1 |
| A/D | 近 20 日 A/D 整体**下行**，且与 OBV **不矛盾** |
| CMF | 最后一根有效 CMF(20) **&lt; -0.1** |
| VWAP | 收盘价 **&lt;** 区间累积 VWAP |

**CMF 中性带**：CMF ∈ [-0.1, 0.1] 时，CMF 子项**不计**多/空票。

**A/D 与 OBV 明显矛盾**（一正斜率一负斜率且均显著）：两边 A/D 子项**均不计票**，并在 `meta.uncertainties` 记录；`risk_level` 至少 `medium`。

### 4.2 综合方向 `direction`

令 `B` = 偏多票合计，`S` = 偏空票合计（各最高 4 票）。

- 若 `B - S >= 2` → `bullish`
- 若 `S - B >= 2` → `bearish`
- 否则 → `neutral`

若有效交易日 &lt; 30：**强制** `neutral`，`confidence` ≤ 0.35。

### 4.3 置信度 `confidence`（0.0～1.0）

在已得 `direction` 且非强制 neutral 时：

| 条件 | confidence 建议区间 |
|------|---------------------|
| `|B - S| == 2` | 0.50～0.65 |
| `|B - S| == 3` | 0.65～0.80 |
| `|B - S| >= 4` | 0.75～0.90 |

**下调**：存在 A/D 与 OBV 矛盾、或单一指标缺失、或成交量异常稀薄 → 在区间基础上 **减 0.10～0.20**，且不低于 0.0。

**强制 neutral** 时：`confidence` 0.25～0.40（视缺失程度）。

### 4.4 风险等级 `meta.risk_level`

- `low`：四指标可计算，票差清晰，无背离与矛盾。
- `medium`：存在背离、或 A/D 与 OBV 轻微不一致、或 CMF 在 [-0.1, 0.1] 且其它指标分裂。
- `high`：数据质量存疑（大量缺失、复权/单位不明）、或多指标强烈冲突且用户要求明确方向。

### 4.5 `meta.time_horizon`

默认 `short`；若用户明确分析季度以上日线趋势且无日内需求，可填 `mid`。

### 4.6 `meta.needs_human_review`

以下任一为 true：

- 必填数据缺失或 &lt; 30 日有效样本
- `risk_level == high`
- VWAP / CMF 无法得到有效终值
- 用户声明用于实盘决策且未提供数据来源说明

---

## 5. 标准输出

最终输出 **JSON**，顶层字段与 `agents.signal.Signal` 对齐；扩展信息放入 `meta`。

```json
{
  "direction": "bullish",
  "confidence": 0.72,
  "reasoning": "一句话到一小段：为何给出该方向与置信度。",
  "signals": [
    "OBV 上升且价在区间 VWAP 上方",
    "CMF(20) 处于弱流入区"
  ],
  "source": "volume_insight",
  "signal_type": "technical",
  "stock_code": "",
  "weight": 1.0,
  "meta": {
    "output_version": "0.1",
    "skill_name": "volume_insight",
    "owner_group": "专家2组（指标）",
    "target": "",
    "period": "YYYY-MM-DD ~ YYYY-MM-DD",
    "time_horizon": "short",
    "risk_level": "medium",
    "key_findings": [],
    "evidence": [
      {
        "source_type": "market_data",
        "source_name": "OHLCV 行情",
        "date": "",
        "metric": "CMF(20) 终值",
        "value": "",
        "comparison": "阈值 ±0.1 / ±0.2",
        "note": ""
      }
    ],
    "risk_notes": [],
    "uncertainties": [],
    "needs_human_review": false,
    "report_markdown": ""
  }
}
```

**说明**：

- `direction` 仅 `bullish` | `bearish` | `neutral`。
- `signal_type` 固定 `technical`。
- `source` 建议填 `volume_insight`（与 `skill_name` 一致便于仲裁）。
- `meta.evidence` 至少 **1 条**，须包含 OBV/CMF/VWAP/A-D 中实际用到的关键数值或定性结论；`source_type` 为行情时用 `market_data`。
- `meta.report_markdown`：若生成完整 Markdown 报告，可放于此；若主仓校验不允许空字符串外扩展，联调前与开发1组确认；否则可省略该键。

---

## 6. 质量检查（输出前自检）

- [ ] `direction` 已填且合法
- [ ] `confidence` ∈ [0.0, 1.0]
- [ ] `signal_type` 为 `technical`
- [ ] `signals` 至少 1 条短句
- [ ] `meta.period`、`meta.time_horizon`、`meta.risk_level` 已填
- [ ] `meta.evidence` 至少 1 条，且与推理一致
- [ ] 数据缺失已写入 `meta.uncertainties`
- [ ] 需人工复核时已设 `meta.needs_human_review: true`

---

## 附录：资源路径（本仓库）

- `references/` — 指标卡片与 `indicator-formulas.md`
- `scripts/` — `compute_obv.py`、`compute_adl.py`、`compute_cmf.py`、`compute_vwap.py`、`analyzer_main.py`
- `assets/report-template.md` — 人类可读报告结构示例
- `assets/sample-output.md` — 填好的报告示例（虚构数据）

主仓规范参见：[SKILL_TEMPLATE.md](https://github.com/duolongworld/AI_Renaissance/blob/develop/docs/SKILL_TEMPLATE.md)。
