# Volume Insight Skill – 量能指标综合分析

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
