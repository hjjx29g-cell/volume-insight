| name | volume-insight |
|------|----------------|
| description | Analyze OBV, A/D Line, CMF, and VWAP volume indicators for stock OHLCV data. Use whenever user mentions volume indicators, money flow, accumulation/distribution, trading volume analysis, OBV, A/D, CMF, VWAP, or asks about "量能分析"/"资金流向"/"成交量指标". Generates a structured report with trends, divergences, intensity ratings, and composite bullish/bearish conclusion. |
| owner_group | 专家2组（指标） |
| domain | technical |
| status | active |
| enabled | false |

# Volume Insight – Four‑Indicator Liquidity & Money Flow Analysis

This skill provides a systematic liquidity diagnosis by integrating four complementary volume‑based indicators: OBV (direction), A/D Line (quality), VWAP (cost baseline), and CMF (intensity & persistence).

## When to Use

Activate this skill when the user:
- Provides a stock code + date range (e.g., "NVDA 2025-01-01 to 2025-12-31")
- Uploads an OHLCV CSV / JSON file (must contain date, open, high, low, close, volume)
- Asks a question that involves one or more of the four indicators
- Mentions "资金流向质量", "背离强度", "平均成本位置", or other volume‑sensitive topics

**Do NOT use** when the user only wants price‑based indicators (e.g., RSI, MACD alone) without any volume context.

## What This Skill Delivers

A Markdown report containing:
1. OBV trend & divergence (顶/底背离) with specific price‑OBV comparison
2. A/D Line direction and consistency check with OBV
3. CMF(20) value + strength rating (strong/weak inflow/outflow)
4. VWAP comparison (close price vs. cumulative volume‑weighted average cost)
5. Composite conclusion (Bullish / Bearish / Neutral) + explicit trade hints

## Step‑by‑Step Execution

1. **Validate and prepare data** – ensure at least 30 trading days, OHLCV format.
2. **Compute OBV** – detect divergence (peak/trough comparison over last 20 days).
3. **Compute A/D Line** – compare trend with OBV, assess consistency.
4. **Compute CMF(20)** – assign strength rating and 5‑day change.
5. **Compute VWAP** – compare last close vs cumulative VWAP over entire interval.
6. **Synthesize composite conclusion** – generate trade suggestions (long/short conditions, stop loss hints).
7. **Output report** following `assets/report-template.md`.

## Output Template Reference

See `assets/report-template.md` for the exact Markdown structure.

## Examples

A complete sample report can be found in `assets/sample-output.md`.

## Resource Files

- `references/` – detailed indicator cards and full formula spec.
- `scripts/` – Python implementations ready to be called by the agent.
- `assets/` – report template and example output.
