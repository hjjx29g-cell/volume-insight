# 量价动量综合分析 Skill - 量能指标系统诊断

本 Skill 提供 OBV、A/D Line、CMF、VWAP 四个核心量能指标的系统化分析；并入 [AI_Renaissance](https://github.com/duolongworld/AI_Renaissance) 时，**唯一规范文件为根目录 `SKILL.md`**。

当前 `SKILL.md` 已按主仓 `docs/ANALYSIS_SKILL_TEMPLATE.md` 的第一阶段 v0.1 结构对齐：顶层输出字段与 `agents.signal.Signal` 对齐，证据、风险等级、时间周期、关键发现、不确定性和人工复核点统一放在 `meta` 中。

## 安装使用

1. 将本仓库复制到主仓推荐路径：`skills/technical/volume_price_momentum_analysis/`（与 `SKILL.md` 中 `name: volume_price_momentum_analysis` 一致）。
2. Agent 联调时读取 **`SKILL.md`**。
3. 提供 OHLCV（CSV 等，至少约 60 个交易日，覆盖 3 个月以上）或股票代码 + 日期范围。

## 示例

`examples/run_example.sh` 演示了如何使用 `sample_data.csv` 生成标准 Signal JSON：

```bash
sh examples/run_example.sh
```

## 目录结构说明

- `SKILL.md` - **主规范**（适用范围、输入、判断规则、标准 Signal JSON）
- `references/` - 指标卡片与公式
- `scripts/` - 指标计算与 `analyzer_main.py`
- `assets/` - Markdown/JSON 报告样例
- `examples/`、`tests/` - 示例与单测

## 依赖

Python 3.7+，numpy。可通过 `pip install numpy` 安装。

## 许可

AI Renaissance 内部使用。
