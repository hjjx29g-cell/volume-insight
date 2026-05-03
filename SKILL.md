---
name: volume_insight
description: 基于 OHLCV 计算 OBV、A/D Line、CMF(20)、区间累积 VWAP 四指标并计票，输出技术面 Signal；在用户提及量能、资金流向、OBV/A/D/CMF/VWAP、量价背离或「量能分析」时启用。
owner_group: 专家2组（指标）
domain: technical
status: draft
---

# 量能四指标综合诊断（volume_insight）

## 1. 适用范围

适用任务：

- 从 OHLCV 判断 **量能偏多 / 偏空 / 中性**，并给出 **置信度、证据、风险等级**，供开发2组仲裁与主流程汇总。
- 适合分析 **个股、ETF、指数** 等具备可靠 **日线（为主）OHLCV** 的标的。
- 适合 **最近 N 个交易日**（建议有效样本 ≥ 30 日）；周线需在 `meta.uncertainties` 说明。

边界说明：

- 缺列、样本不足、复权/成交量口径不明时，须 **降低 `confidence`**、**标 `needs_human_review`**，在 `meta.uncertainties` 写明。
- 小盘股（流通市值<50亿）或庄股需人工复核，指标容易被操纵。
- 重大消息日、停牌复牌首日指标失真，标记人工复核。
- 本 Skill 仅覆盖 **技术量能维度**，**不替代**基本面、公告与消息面；结论 **不构成投资建议**；`risk_level` 较高或需复核时，**不得单独**作为交易指令。

## 2. 输入材料

### 必填输入

- **标的**：公司名 / 股票代码 / 指数代码（无代码可将名称写入 `meta.target`）
- **时间范围**：分析区间起止日期，与 OHLCV 对齐
- **核心数据材料**：**行情 OHLCV**（每行至少 `date, open, high, low, close, volume`；列名可映射，须在 `meta.uncertainties` 说明）
- **数据来源**：行情终端、CSV/JSON 上传、开发3组行情接口等（证据中 `source_type` 用 `market_data`）

### 缺失处理

- 若 **必填 OHLCV 缺失任一行、或可解析有效交易日 &lt; 30**：输出 `direction: "neutral"`，**降低 `confidence`**（建议 ≤ 0.35），在 `meta.uncertainties` 写明缺什么，**`meta.needs_human_review: true`**。
- 若 **VWAP 无法计算**（如成交量累加为 0）：该子规则不计票，写入 `uncertainties`；多指标同时失效时 **`needs_human_review: true`**。
- 若 **可选输入缺失**：可继续分析，在 `meta.uncertainties` 说明可能影响。

## 3. 分析步骤

按下面步骤分析：

1. 明确分析对象、时间范围和数据来源（复权、成交量单位写入证据或 `uncertainties`）。
2. 检查输入数据是否足够（有效交易日 ≥ 30；不足则按 §2 缺失处理降级）。
3. 提取关键指标：计算或调用 `scripts/` 得到 **OBV、A/D Line、CMF(20)、区间累积 VWAP**（CMF 取最后一根有效值）；**20 日**内判断价 vs OBV **顶/底背离**；**20 日**内判断 A/D 与 OBV **同向或矛盾**。
4. 按 **§4 判断规则** 计偏多票 `B`、偏空票 `S`，映射 **`direction`**，并按票差与矛盾情况给出 **`confidence`**、**`meta.risk_level`**。
5. 给出证据：每条关键结论对应 **`meta.evidence`**（指标名、数值或定性、对比阈值、数据来源日期）。
6. 标注 **`meta.uncertainties`**、**`meta.needs_human_review`**、**`meta.time_horizon`**（默认 `short`，较长日线趋势可 `mid`）。
7. 输出 **标准 JSON**（§5 结构）。

**实现约定**：本仓库 **VWAP** 为 **日线区间累积**（典型价 (H+L+C)/3），**不是**「每交易日重置的日内 VWAP」；证据与表述中用 **「区间 VWAP」**。详见 `scripts/compute_vwap.py`、`references/`。

## 4. 判断规则

本 Skill 的专业规则为 **四维度计票**（OBV、A/D、CMF、VWAP），再合成方向与置信度。每条子规则须写清：

| 要素 | 本 Skill 约定 |
|------|----------------|
| 判断指标 | OBV 趋势与背离、A/D 20 日方向、CMF(20) 末值、收盘价 vs 区间 VWAP |
| 阈值或比较对象 | CMF 与 ±0.1 分界；票差与 2 比较 |
| 时间窗口 | OBV **5 日**趋势与 **20 日**背离；A/D **20 日** |
| 对 `direction` 的影响 | 由 `B−S` 与 2 的关系决定 bull/bear/neutral |
| 对 `confidence`、`risk_level` 的影响 | 见 §4.3、§4.4；A/D 与 OBV 显著矛盾时降置信、`risk_level` 至少 `medium` |

**规则摘要**：

- 若 **A/D 与 OBV 显著矛盾**：A/D 相关 **不计票**，`neutral` 倾向增强，**降低 `confidence`**，`meta.uncertainties` 写明矛盾。
- 若 **CMF ∈ [-0.1, 0.1]**：CMF 维度 **不计票**。
- 若 **指标互相矛盾** 或 **证据不足**：输出 `neutral` 或降低置信，**`needs_human_review: true`**。

### 4.1 计票（每维度最多 1 票）

令 **B** = 偏多票合计，**S** = 偏空票合计（各 ≤ 4）。

**偏多 +1**：

| 维度 | 条件 |
|------|------|
| OBV | 近 5 日相对上升，**或** 20 日内 **底背离**（价创新低 OBV 未新低）；二选一不重复计 |
| A/D | 近 20 日整体抬升，且与 OBV **不显著矛盾** |
| CMF | CMF(20) 末值 **&gt; 0.1** |
| VWAP | 收盘价 **&gt;** 区间累积 VWAP（序列最后一根） |

**偏空 +1**：

| 维度 | 条件 |
|------|------|
| OBV | 近 5 日下降，**或** 20 日内 **顶背离** |
| A/D | 近 20 日整体下行，且与 OBV **不显著矛盾** |
| CMF | CMF(20) 末值 **&lt; -0.1** |
| VWAP | 收盘价 **&lt;** 区间 VWAP |

**显著矛盾**：A/D 与 OBV 一正一负且斜率均显著时，**A/D 两行均不计票**，`risk_level` 至少 **medium**。

### 4.2 `direction`

- `B − S ≥ 2` → `bullish`
- `S − B ≥ 2` → `bearish`
- 否则 → `neutral`
- 有效交易日 **&lt; 30**：**强制** `neutral`，`confidence` ≤ 0.35

### 4.3 `confidence`（0.0～1.0）

非强制 `neutral` 时，按 **票差绝对值**（B 与 S 之差的绝对值）：

| 票差绝对值 | 建议区间 |
|------------|----------|
| 2 | 0.50～0.65 |
| 3 | 0.65～0.80 |
| ≥ 4 | 0.75～0.90 |

存在 A/D 与 OBV 矛盾、单指标缺失、量能过薄：在区间内 **减 0.10～0.20**。强制 `neutral`：**0.25～0.40**。

### 4.4 `meta.risk_level`

- **low**：四指标可算，票差清晰，无硬矛盾  
- **medium**：有背离、A/D 与 OBV 轻度不一致、或 CMF 中性且其它指标分裂  
- **high**：数据口径存疑、或多指标激烈冲突且用户强求方向  

### 4.5 `meta.needs_human_review`

缺必填数据、&lt;30 日、`risk_level: high`、VWAP/CMF 无有效终值、用户声明实盘但无来源说明等 → **true**

### 从自然语言翻译成 Skill 规则（技术面示例）

```text
盘面判断：
价格创 20 日新高，但 OBV 未创新高，怀疑量价顶背离。
```

翻译成 Skill 规则：

```text
指标：收盘价极值 vs OBV 极值（20 日窗口）
阈值：价新高且 OBV 未新高 → 顶背离成立
direction：为计票贡献偏空票 +1（若同时满足 OBV 下降则仍只计一次该维度）
confidence：若仅单一背离、其余指标中性，不宜高于 0.65；需写入 meta.evidence 与 uncertainties
risk_level：至少 medium（背离）
evidence：记录窗口起止、价与 OBV 峰值日期与数值、OHLCV 来源
needs_human_review：若数据复权或切片边界不清 → true
```

## 5. 标准输出

最终输出 JSON，顶层字段与当前项目 `agents.signal.Signal` 对齐。当前代码已经支持的字段放在顶层；给开发2组后续仲裁、展示、追溯使用的补充字段，先放在 `meta` 中。

这里的 `meta` 是 Skill 输出的一部分，不是可有可无的附注。第一阶段 v0.1 规范中，证据、风险等级、时间周期、关键发现、不确定性和人工复核点统一放在 `meta` 中。

本 Skill 须写清楚：

- **证据从哪里来**：OHLCV 行情 → `source_type: market_data`  
- **风险等级如何判断**：§4.4  
- **时间周期如何判断**：默认 `short`，较长日线趋势可 `mid`（§4 已述）  
- **关键发现如何提取**：3～5 条写入 `meta.key_findings`  
- **何时人工复核**：§4.5  

Agent 读取本 Skill 后，按上述规则生成 JSON；开发2组汇总仲裁时读取 `meta` 中证据与上下文。后续若 `output_version` 变更，由开发1组统一发布。

```json
{
  "direction": "bullish | bearish | neutral",
  "confidence": 0.0,
  "reasoning": "",
  "signals": [],
  "source": "volume_insight",
  "signal_type": "technical",
  "stock_code": "",
  "weight": 1.0,
  "meta": {
    "output_version": "0.1",
    "skill_name": "volume_insight",
    "owner_group": "专家2组（指标）",
    "target": "",
    "period": "",
    "time_horizon": "short | mid | long",
    "risk_level": "low | medium | high",
    "key_findings": [],
    "evidence": [
      {
        "source_type": "financial_report | announcement | market_data | fund_flow | macro_data | industry_data | news | social_media | research_report | expert_input",
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

**说明**：

- `direction` 只能是 `bullish`、`bearish`、`neutral`。当前代码暂不支持 `risk_warning` 作为方向。
- 本 Skill 固定 **`signal_type: "technical"`**；`source` 建议填 **`volume_insight`**（与 `skill_name` 一致）。
- `confidence` 范围 0.0～1.0。
- `signals` 写核心短句（如「CMF(20) 弱流入 + 价上区间 VWAP」）。
- `reasoning` 写简明推理；**详细数值与对比**进 `meta.evidence`。
- 可选：将人类可读 Markdown 报告（见 `assets/report-template.md`）作为联调扩展放入 `meta` 额外字段前，**与开发1组确认**是否纳入 Schema。

### 填写示例（本 Skill 典型一条 evidence）

```json
{
  "source_type": "market_data",
  "source_name": "OHLCV 日线",
  "date": "2026-04-30",
  "metric": "CMF(20) 终值",
  "value": "0.15",
  "comparison": "> 0.1 偏多计票阈值",
  "note": "与 OBV 5 日上升、收盘 > 区间 VWAP 一致"
}
```

## 字段中英对照

| 字段 | 中文含义 | 填写说明 |
|---|---|---|
| `direction` | 方向 | `bullish` 看多；`bearish` 看空；`neutral` 中性 |
| `confidence` | 置信度 | 0.0 到 1.0，越高表示越确定 |
| `reasoning` | 推理摘要 | 用一小段话说明为什么得出这个结论 |
| `signals` | 核心信号 | 放最重要的短句 |
| `source` | 信号来源 | 本 Skill 填 `volume_insight` |
| `signal_type` | 信号类型 | 本 Skill 固定 `technical` |
| `stock_code` | 股票代码 | 没有时可留空，标的写入 `meta.target` |
| `weight` | 权重 | 先填 1.0，后续由仲裁层决定 |
| `meta` | 证据包/上下文包 | 证据、风险等级、时间周期、人工复核点等 |
| `time_horizon` | 时间周期 | `short` 短期；`mid` 中期；`long` 长期 |
| `risk_level` | 风险等级 | `low` 低；`medium` 中；`high` 高 |
| `evidence` | 证据 | 记录来源、日期、指标、数值和说明 |
| `uncertainties` | 不确定性 | 数据缺失、口径不一致、需要复核的地方 |
| `needs_human_review` | 是否需要人工复核 | `true` 是；`false` 否 |

## `source_type` 来源类型

本 Skill **以 `market_data` 为主**；若证据含研报、新闻等，按实际类型填写。

| source_type | 中文含义 | 示例 |
|---|---|---|
| `financial_report` | 财报 | 年报、季报、现金流量表 |
| `announcement` | 公告 | 交易所公告、重大事项 |
| `market_data` | 行情数据 | **OHLCV、本 Skill 四指标计算结果** |
| `fund_flow` | 资金流数据 | 主力资金、北向资金 |
| `macro_data` | 宏观数据 | 利率、PMI、CPI |
| `industry_data` | 行业数据 | 产业链价格、开工率 |
| `news` | 新闻 | 财经新闻、政策新闻 |
| `social_media` | 社交舆情 | 股吧、雪球 |
| `research_report` | 研报 | 券商研报 |
| `expert_input` | 人工输入 | 专家组补充材料 |

## `domain`、`source`、`source_type` 的区别

| 字段 | 一句话解释 | 本 Skill 示例 |
|---|---|---|
| `domain` | Skill 所属专家领域 | `technical`（frontmatter 与主仓一致） |
| `source` | 谁产出这条信号 | `volume_insight` |
| `source_type` | 某条证据来自什么材料 | 行情计算 → `market_data` |

## 方向、置信度、风险等级怎么判断

### `direction` 方向映射

- 票差偏多、四指标共振偏多：`bullish`
- 票差偏空、共振偏空：`bearish`
- 票差不足、数据不足、或指标冲突：`neutral`
- 风险提示不单独新增方向；用 `signal_type` 与 `meta.risk_notes` 表达。

### `confidence` 置信度分档（结合 §4.3）

- **0.75～0.90**：票差大（绝对值 ≥ 4）、证据一致、无矛盾  
- **0.65～0.80**：票差 3、少量不确定性  
- **0.50～0.65**：票差 2、或存在轻微分歧  
- **&lt; 0.4**：强制 `neutral` 或证据不足，配合 `needs_human_review`

**技术面补充**：单一背离、其余中性时，不宜给过高置信度；A/D 与 OBV 矛盾须 **下调**。

### `risk_level` 风险等级分档

- **low**：指标可算、票差清晰、无显著矛盾  
- **medium**：背离、A/D 与 OBV 不一致、或 CMF 中性带内且其它分裂  
- **high**：数据质量存疑、或强烈冲突且用户强求结论  

### `time_horizon` 时间周期

- 本 Skill 默认 **`short`**（日线量能、数周尺度）  
- 明确分析 **数月以上日线趋势** 且无日内需求时可 **`mid`**  
- 一般 **`long`** 留给宏观/产业周期类 Skill；本 Skill 少用  

## 6. 质量检查

输出前检查：

- [ ] 是否有明确 `direction`
- [ ] `confidence` 是否在 0.0 到 1.0
- [ ] 是否写明 `signal_type`（本 Skill 为 `technical`）
- [ ] 是否有至少一条核心 `signals`
- [ ] 是否有证据来源（`meta.evidence` 至少 1 条）
- [ ] 是否标注 `meta.time_horizon` 与 `meta.risk_level`
- [ ] 缺失数据是否写进 `meta.uncertainties`
- [ ] 是否需要人工复核（`needs_human_review`）

---

## 附录：本仓库资源

| 路径 | 用途 |
|------|------|
| `references/` | 指标释义与 `indicator-formulas.md` |
| `scripts/` | `compute_*.py`、`analyzer_main.py` |
| `assets/report-template.md` | 可选人类可读报告结构 |

主仓模板原文：[SKILL_TEMPLATE.md](https://github.com/duolongworld/AI_Renaissance/blob/develop/docs/SKILL_TEMPLATE.md)
