# Volume Insight Skill – 量能指标综合分析

本 Skill 提供 OBV、A/D Line、CMF、VWAP 四个核心量能指标的系统化分析；并入 [AI_Renaissance](https://github.com/duolongworld/AI_Renaissance) 时，**唯一规范文件为根目录 `SKILL.md`**（YAML frontmatter + `Signal` JSON 契约，与主仓 `docs/SKILL_TEMPLATE.md` 对齐）。

## 安装使用

1. 将本仓库复制到主仓推荐路径：`skills/technical/volume_insight/`（与 `SKILL.md` 中 `name: volume_insight` 一致）。
2. Agent 联调时读取 **`SKILL.md`**。
3. 提供 OHLCV（CSV 等，至少约 30 个交易日）或股票代码 + 日期范围。

## 示例

`examples/run_example.sh` 演示了如何使用 sample_data.csv 进行分析。

## 目录结构说明

- `SKILL.md` — **主规范**（适用范围、输入、判断规则、标准 JSON）
- `references/` — 指标卡片与公式
- `scripts/` — 指标计算与 `analyzer_main.py`
- `assets/` — Markdown 报告模板（可与 `meta.report_markdown` 联调）
- `examples/`、`tests/` — 示例与单测

## 依赖

Python 3.7+，pandas，numpy。可通过 `pip install pandas numpy` 安装。

## 许可

AI Renaissance 内部使用。
