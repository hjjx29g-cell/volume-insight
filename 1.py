import os

# ============================================================
# 完整的 volume-insight Skill 生成脚本（兼容 AI Renaissance 规范）
# ============================================================

files = {
    "SKILL.md": '''| name | volume-insight |
|------|----------------|
| description | Analyze OBV, A/D Line, CMF, and VWAP volume indicators for stock OHLCV data. Use whenever user mentions volume indicators, money flow, accumulation/distribution, trading volume analysis, OBV, A/D, CMF, VWAP, or asks about "量能分析"/"资金流向"/"成交量指标". Generates a structured report with trends, divergences, intensity ratings, and composite bullish/bearish conclusion. |
| owner_group | 专家2组（指标） |
| domain | technical |
| status | active |
| enabled | true |

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
''',

    "references/obv-card.md": '''# OBV（能量潮 – On Balance Volume）

## 计算公式
OBV = 前一日 OBV ± 当日成交量  
- 收盘价 > 前日收盘价：加成交量  
- 收盘价 < 前日收盘价：减成交量  
- 收盘价 = 前日收盘价：不变  

## 核心逻辑
量先价行，累加成交量反映资金净流向和人气强弱。

## 实战看点与判读标准
- **顶背离**：股价新高，OBV 未新高 → 上涨动能减弱，卖出信号  
- **底背离**：股价新低，OBV 未新低 → 抛压减轻，买入信号  
- **同步上涨**：量价齐升，趋势健康  
- **OBV 横盘后突破**：长期横盘后向上突破 → 多方爆发，买入信号  

## 操作启示
背离信号需等待“二次确认”（如价格突破颈线或 OBV 趋势线被突破）再操作。

## 局限性
不考虑日内价格位置，跳空缺口可能误导。成交量稀薄时易失真。
''',

    "references/adl-card.md": '''# A/D Line（累积/派发线 – Accumulation/Distribution Line）

## 计算公式
MFM = [ (收盘价–最低价) – (最高价–收盘价) ] / (最高价–最低价)  
MFV = MFM × 成交量  
A/D = 前一日 A/D + MFV  
涨跌停时 MFM = 收盘价/昨收 – 1。

## 核心逻辑
收盘价越接近最高价 → MFM 越接近 +1 → 资金积累（买入）  
收盘价越接近最低价 → MFM 越接近 -1 → 资金派发（卖出）

## 实战看点
- **同步上升**：股价与 A/D 同步新高 → 真突破  
- **顶背离**：股价新高，A/D 未新高 → 主力派发  
- **底背离**：股价新低，A/D 未新低 → 主力吸筹  
- **突破验证**：价格突破阻力位时，A/D 也同步突破 → 真突破  

## 与 OBV 差异
OBV 看方向（粗），A/D 看质量（细）。

## 局限性
跳空缺口失真，横盘行情噪音多。
''',

    "references/vwap-card.md": '''# VWAP（成交量加权平均价 – Volume Weighted Average Price）

> **注意**：VWAP 属于日内执行成本基准指标，与 OBV/A/D 的用法不同，主要用于判断当前价格相对于当天平均成交成本的高低。

## 计算公式
VWAP = Σ(成交价 × 成交量) / Σ(成交量)  
典型价格 = (最高+最低+收盘)/3

## 核心逻辑
反映全体市场参与者当天的平均成交成本。机构用作执行基准。

## 实战看点
- **价格 > VWAP** → 市场强势（多数人获利）  
- **价格 < VWAP** → 市场弱势（多数人被套）  
- **支撑/阻力**：价格回踩 VWAP 不破 → 支撑；反弹至 VWAP 遇阻 → 阻力  
- **突破信号**：放量从下向上穿过 VWAP 并站稳 → 短期转强  

## 操作启示
不作为唯一买卖信号，需结合成交量、K 线形态及其他指标。

## 局限性
仅适用于高流动性品种，日内指标过夜重置，有滞后性。
''',

    "references/cmf-card.md": '''# CMF（钱流量 – Chaikin Money Flow）

## 计算公式
CMF = Σ(MFV) over n 天 / Σ(Volume) over n 天 （常用 n=20）  
MFM 和 MFV 的定义与 A/D 线相同。

## 核心逻辑
衡量一段时期内资金净流入/流出的强度，范围 [-1, +1]。

## 判读标准
| CMF 范围 | 含义 |
|---|---|
| > +0.2 | 强流入，强烈看多 |
| +0.1 ~ +0.2 | 弱流入，温和看多 |
| -0.1 ~ +0.1 | 中性，震荡 |
| -0.2 ~ -0.1 | 弱流出，温和看空 |
| < -0.2 | 强流出，强烈看空 |

- **背离**：价格新高但 CMF 低于前高 → 顶背离；价格新低但 CMF 高于前低 → 底背离。

## 与其他指标配合
OBV 定方向 → A/D 定质量 → CMF 定强度。

## 局限性
固定时间窗口可能滞后，横盘市中假信号多。
''',

    "references/indicator-formulas.md": '''# 四个量能指标统一公式手册

## OBV
OBV_t = OBV_{t-1} + (Volume_t if Close_t > Close_{t-1} else -Volume_t if Close_t < Close_{t-1} else 0)

## A/D Line
MFM_t = ( (Close_t - Low_t) - (High_t - Close_t) ) / (High_t - Low_t)   # 若 High==Low 则 MFM = Close_t/Close_{t-1} - 1  
MFV_t = MFM_t × Volume_t  
ADL_t = ADL_{t-1} + MFV_t

## CMF (20-day)
CMF_t = sum_{i=t-19}^{t} MFV_i / sum_{i=t-19}^{t} Volume_i

## VWAP (cumulative over entire interval)
VWAP = sum( TypicalPrice_i × Volume_i ) / sum( Volume_i )  
TypicalPrice_i = (High_i + Low_i + Close_i) / 3
''',

    "scripts/compute_obv.py": '''import numpy as np

def compute_obv(close, volume):
    obv = np.zeros(len(close))
    for i in range(1, len(close)):
        if close[i] > close[i-1]:
            obv[i] = obv[i-1] + volume[i]
        elif close[i] < close[i-1]:
            obv[i] = obv[i-1] - volume[i]
        else:
            obv[i] = obv[i-1]
    return obv
''',

    "scripts/compute_adl.py": '''import numpy as np

def compute_adl(high, low, close, volume):
    adl = np.zeros(len(close))
    for i in range(len(close)):
        if high[i] == low[i]:
            if i == 0:
                mfm = 0
            else:
                mfm = close[i] / close[i-1] - 1
        else:
            mfm = ((close[i] - low[i]) - (high[i] - close[i])) / (high[i] - low[i])
        mfv = mfm * volume[i]
        adl[i] = adl[i-1] + mfv if i > 0 else mfv
    return adl
''',

    "scripts/compute_cmf.py": '''import numpy as np

def compute_cmf(high, low, close, volume, window=20):
    mfv = np.zeros(len(close))
    for i in range(len(close)):
        if high[i] == low[i]:
            mfm = close[i] / close[i-1] - 1 if i > 0 else 0
        else:
            mfm = ((close[i] - low[i]) - (high[i] - close[i])) / (high[i] - low[i])
        mfv[i] = mfm * volume[i]
    cmf = np.full(len(close), np.nan)
    for i in range(window-1, len(mfv)):
        sum_mfv = np.sum(mfv[i-window+1:i+1])
        sum_vol = np.sum(volume[i-window+1:i+1])
        cmf[i] = sum_mfv / sum_vol if sum_vol != 0 else 0
    return cmf
''',

    "scripts/analyzer_main.py": '''import pandas as pd
import numpy as np
from compute_obv import compute_obv
from compute_adl import compute_adl
from compute_cmf import compute_cmf

def compute_vwap(typical_prices, volumes):
    cum_pv = np.sum(typical_prices * volumes)
    cum_vol = np.sum(volumes)
    return cum_pv / cum_vol if cum_vol != 0 else np.nan

def analyze(df):
    """
    df: DataFrame with columns 'high','low','close','volume' (date index optional)
    Returns dict with all indicator values and basic interpretation.
    """
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    volume = df['volume'].values

    obv = compute_obv(close, volume)
    adl = compute_adl(high, low, close, volume)
    cmf = compute_cmf(high, low, close, volume, window=20)
    typical = (high + low + close) / 3
    vwap = compute_vwap(typical, volume)

    last_close = close[-1]
    last_obv_trend = "上升" if len(obv)>5 and obv[-1] > obv[-5] else "下降"
    cmf_last = cmf[-1] if not np.isnan(cmf[-1]) else 0
    if cmf_last > 0.2:
        cmf_rating = "强流入"
    elif cmf_last > 0.1:
        cmf_rating = "弱流入"
    elif cmf_last > -0.1:
        cmf_rating = "中性"
    elif cmf_last > -0.2:
        cmf_rating = "弱流出"
    else:
        cmf_rating = "强流出"

    price_vs_vwap = "高于" if last_close > vwap else "低于"

    return {
        "obv_trend": last_obv_trend,
        "adl_last": adl[-1],
        "cmf_last": cmf_last,
        "cmf_rating": cmf_rating,
        "vwap": vwap,
        "price_vs_vwap": price_vs_vwap,
        "close": last_close
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        df = pd.read_csv(sys.argv[1], parse_dates=['date'], index_col='date')
        res = analyze(df)
        print(res)
''',

    "assets/report-template.md": '''# 📊 量能综合分析报告 – {股票名称/代码}
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
''',

    "assets/sample-output.md": '''# 📊 量能综合分析报告 – 示例公司 (TEST)
**分析周期**：2025-01-02 至 2026-04-30（共 320 个交易日）

## 1️⃣ OBV – 资金方向
- 趋势：上升
- 背离信号：无
- 解读：OBV 持续走高，资金总体净流入，与价格同步上涨，量价健康。

## 2️⃣ A/D Line – 资金质量
- 趋势：累积（上升）
- 背离信号：无
- 与 OBV 一致性：一致，确认资金流入质量良好。

## 3️⃣ CMF(20) – 资金强度
- 当前值：+0.23
- 评级：强流入
- 近期变化：近 5 期 CMF 从 +0.18 升至 +0.23，强度增强。

## 4️⃣ VWAP – 成本基准
- 区间 VWAP：105.30
- 最新收盘价：110.20（高于 VWAP）
- 含义：当前价格高于市场平均成本，多方占据优势。

## 5️⃣ 综合结论与操作启示
- **综合评级**：强烈看多
- **关键逻辑**：OBV 趋势向上、CMF 强正、A/D 累积、价格高于 VWAP，四指标共振偏多。
- **操作建议**：
  - 做多条件：价格回踩 VWAP (约105.30) 且 CMF 保持 >+0.1 时加仓。
  - 做空/离场条件：跌破 OBV 上升趋势线或 CMF 转负。
  - 止损参考：收盘价跌破最近 20 日低点。

## 6️⃣ 数据附录（最近5日）
| 日期 | OBV | A/D | CMF | VWAP |
|------|-----|-----|-----|------|
| 2026-04-24 | 15.2M | 8.1M | +0.21 | 105.10 |
| 2026-04-25 | 15.5M | 8.3M | +0.22 | 105.15 |
| 2026-04-26 | 15.7M | 8.5M | +0.22 | 105.20 |
| 2026-04-29 | 16.0M | 8.7M | +0.23 | 105.25 |
| 2026-04-30 | 16.2M | 8.9M | +0.23 | 105.30 |
''',

    "examples/sample_data.csv": '''date,open,high,low,close,volume
2025-01-02,100,102,99,101,1000000
2025-01-03,101,103,100,102,1100000
2025-01-04,102,105,101,104,1200000
2025-01-05,104,106,103,105,1150000
2025-01-06,105,107,104,106,1300000
2025-01-07,106,108,105,107,1250000
2025-01-08,107,109,106,108,1400000
2025-01-09,108,110,107,109,1350000
2025-01-10,109,111,108,110,1500000
''',

    "examples/run_example.sh": '''#!/bin/bash
cd "$(dirname "$0")"
python ../scripts/analyzer_main.py sample_data.csv
''',

    "tests/test_indicators.py": '''import unittest
import numpy as np
import sys
sys.path.append('../scripts')
from compute_obv import compute_obv
from compute_adl import compute_adl

class TestVolumeIndicators(unittest.TestCase):
    def test_obv_basic(self):
        close = np.array([10, 11, 10, 12])
        volume = np.array([100, 200, 150, 300])
        obv = compute_obv(close, volume)
        expected = [0, 200, 50, 350]
        np.testing.assert_array_equal(obv, expected)

    def test_adl_basic(self):
        high = np.array([11, 12, 11, 13])
        low = np.array([9, 10, 9, 11])
        close = np.array([10, 11, 10, 12])
        volume = np.array([100, 200, 150, 300])
        adl = compute_adl(high, low, close, volume)
        self.assertEqual(len(adl), len(close))

if __name__ == '__main__':
    unittest.main()
''',

    "tests/fixtures/known_series.csv": '''date,open,high,low,close,volume
2025-01-01,100,101,99,100,1000
2025-01-02,100,102,100,101,1100
2025-01-03,101,103,101,102,1200
''',

    "README.md": '''# Volume Insight Skill – 量能指标综合分析

本 Skill 提供 OBV、A/D Line、CMF、VWAP 四个核心量能指标的系统化分析，生成包含资金方向、质量、强度和成本基准的综合报告。

## 安装使用

1. 将本仓库根目录（含 `SKILL.md`、`references/` 等）复制或克隆到 `AI_Renaissance/skills/technical/volume-insight/`（或按你们规范放到对应 skills 目录）。
2. 确保 Agent 能读取 SKILL.md 表格元数据。
3. 提供 OHLCV 数据（CSV 格式，至少30行）或股票代码+日期范围。

## 示例

`examples/run_example.sh` 演示了如何使用 sample_data.csv 进行分析。

## 目录结构说明

- `SKILL.md` – 核心指令文件（表格元数据 + Markdown）
- `references/` – 指标详细知识卡片
- `scripts/` – 指标计算 Python 脚本
- `assets/` – 报告模板和示例输出
- `examples/` – 示例数据及运行脚本
- `tests/` – 单元测试

## 依赖

Python 3.7+，pandas，numpy。可通过 `pip install pandas numpy` 安装。

## 许可

AI Renaissance 内部使用。
''',

    ".gitignore": '''__pycache__/
*.pyc
*.DS_Store
.venv/
''',
}

def create_skill():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    for filepath, content in files.items():
        full_path = os.path.normpath(os.path.join(root_dir, filepath))
        parent = os.path.dirname(full_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created: {full_path}")

    print("\n✅ volume-insight skill 已完整生成（与 1.py 同目录）！")
    print("目录结构：")
    for root, dirs, filenames in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".venv")]
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        label = os.path.basename(root) or os.path.basename(root_dir.rstrip(os.sep))
        print(f"{indent}{label}/")
        subindent = ' ' * 2 * (level + 1)
        for file in filenames:
            print(f"{subindent}{file}")

if __name__ == "__main__":
    create_skill()