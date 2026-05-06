import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

from compute_obv import compute_obv
from compute_adl import compute_adl
from compute_cmf import compute_cmf
from compute_vwap import compute_vwap


SKILL_NAME = "volume_price_momentum_analysis"
OWNER_GROUP = "专家2组（指标）"


def _to_float(value):
    if value is None or value == "":
        return math.nan
    return float(value)


def load_ohlcv_csv(path):
    rows = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"date", "high", "low", "close", "volume"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
        for row in reader:
            rows.append(
                {
                    "date": row.get("date", ""),
                    "high": _to_float(row.get("high")),
                    "low": _to_float(row.get("low")),
                    "close": _to_float(row.get("close")),
                    "volume": _to_float(row.get("volume")),
                }
            )
    return rows


def _column(rows, name):
    return np.asarray([row[name] for row in rows], dtype=float)


def _slope(values, window=20):
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) < 2:
        return 0.0
    tail = arr[-min(window, len(arr)) :]
    x = np.arange(len(tail), dtype=float)
    return float(np.polyfit(x, tail, 1)[0])


def _pct_change(values, window=20):
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) <= 1:
        return 0.0
    start = arr[-min(window, len(arr))]
    end = arr[-1]
    if start == 0:
        return 0.0
    return float((end - start) / start)


def _cmf_zone(cmf_value):
    if cmf_value > 0.25:
        return "strong_inflow", "强势流入"
    if cmf_value > 0.05:
        return "mild_inflow", "温和流入"
    if cmf_value >= -0.05:
        return "neutral", "中性"
    if cmf_value >= -0.25:
        return "mild_outflow", "温和流出"
    return "strong_outflow", "强势流出"


def _indicator_direction(score):
    if score > 0:
        return "bullish"
    if score < 0:
        return "bearish"
    return "neutral"


def _round(value, digits=4):
    if isinstance(value, (float, np.floating)) and not math.isfinite(float(value)):
        return None
    return round(float(value), digits)


def analyze(rows, stock_code="", target="", source_name="uploaded_csv"):
    """
    Return a Signal-compatible JSON dict for OHLCV rows.
    Required row keys: date, high, low, close, volume.
    """
    if not rows:
        return _neutral_signal(
            stock_code=stock_code,
            target=target,
            source_name=source_name,
            uncertainty="OHLCV 数据为空，无法计算量价指标。",
        )

    high = _column(rows, "high")
    low = _column(rows, "low")
    close = _column(rows, "close")
    volume = _column(rows, "volume")
    dates = [row.get("date", "") for row in rows]

    uncertainties = []
    risk_notes = []
    needs_review = False

    required_arrays = {"high": high, "low": low, "close": close, "volume": volume}
    invalid_fields = [name for name, arr in required_arrays.items() if np.isnan(arr).any()]
    if invalid_fields:
        uncertainties.append(f"必填字段存在缺失或非数字值：{', '.join(invalid_fields)}。")
        needs_review = True

    zero_volume_count = int(np.sum(volume == 0))
    if zero_volume_count:
        uncertainties.append(f"存在 {zero_volume_count} 个成交量为 0 的交易日，相关日期不参与强信号确认。")
        needs_review = True

    obv = compute_obv(close, volume)
    adl = compute_adl(high, low, close, volume)
    cmf = compute_cmf(high, low, close, volume, window=20)
    vwap = compute_vwap(high, low, close, volume)

    last_close = float(close[-1])
    last_volume = float(volume[-1])
    last_obv = float(obv[-1])
    last_adl = float(adl[-1])
    last_vwap = float(vwap[-1]) if len(vwap) else math.nan
    cmf_last = float(cmf[-1]) if len(cmf) and math.isfinite(float(cmf[-1])) else 0.0
    cmf_zone, cmf_label = _cmf_zone(cmf_last)

    price_slope = _slope(close)
    obv_slope = _slope(obv)
    adl_slope = _slope(adl)
    price_change_20d = _pct_change(close)
    vwap_deviation = (last_close - last_vwap) / last_vwap if last_vwap else 0.0

    sub_signals = {}
    score = 0
    signals = []
    key_findings = []

    obv_score = 1 if obv_slope > 0 and price_slope >= 0 else -1 if obv_slope < 0 and price_slope <= 0 else 0
    sub_signals["obv"] = {
        "signal": "OBV趋势上升" if obv_slope > 0 else "OBV趋势下降" if obv_slope < 0 else "OBV趋势不明",
        "direction": _indicator_direction(obv_score),
        "confidence": 0.6 if obv_score else 0.45,
        "latest_value": _round(last_obv, 2),
        "slope_20d": _round(obv_slope, 2),
    }
    score += obv_score

    adl_score = 1 if adl_slope > 0 and price_slope >= 0 else -1 if adl_slope < 0 and price_slope <= 0 else 0
    sub_signals["ad_line"] = {
        "signal": "A/D累积上升" if adl_slope > 0 else "A/D派发下降" if adl_slope < 0 else "A/D趋势不明",
        "direction": _indicator_direction(adl_score),
        "confidence": 0.6 if adl_score else 0.45,
        "latest_value": _round(last_adl, 2),
        "slope_20d": _round(adl_slope, 2),
    }
    score += adl_score

    vwap_score = 1 if vwap_deviation > 0.02 else -1 if vwap_deviation < -0.02 else 0
    sub_signals["vwap"] = {
        "signal": "价格站上VWAP" if vwap_score > 0 else "价格跌破VWAP" if vwap_score < 0 else "价格围绕VWAP震荡",
        "direction": _indicator_direction(vwap_score),
        "confidence": 0.62 if vwap_score else 0.5,
        "latest_value": _round(last_vwap, 4),
        "price_deviation_pct": _round(vwap_deviation * 100, 2),
    }
    score += vwap_score

    cmf_score = 1 if cmf_last > 0.05 else -1 if cmf_last < -0.05 else 0
    sub_signals["cmf"] = {
        "signal": f"CMF{cmf_label}",
        "direction": _indicator_direction(cmf_score),
        "confidence": 0.65 if abs(cmf_last) > 0.25 else 0.58 if cmf_score else 0.5,
        "latest_value": _round(cmf_last, 4),
        "zone": cmf_zone,
    }
    score += cmf_score

    bullish_count = sum(1 for item in sub_signals.values() if item["direction"] == "bullish")
    bearish_count = sum(1 for item in sub_signals.values() if item["direction"] == "bearish")
    direction = "bullish" if score > 1 else "bearish" if score < -1 else "neutral"

    if bullish_count >= 3:
        signals.append("多指标共振偏多")
        key_findings.append("OBV、A/D、VWAP、CMF 中至少 3 个指标偏多。")
    elif bearish_count >= 3:
        signals.append("多指标共振偏空")
        key_findings.append("OBV、A/D、VWAP、CMF 中至少 3 个指标偏空。")
    else:
        signals.append("指标信号分化")
        key_findings.append("量价指标未形成三指标同向共振。")
        if bullish_count and bearish_count:
            uncertainties.append("存在多空指标冲突，需要结合价格位置和市场背景复核。")
            needs_review = True

    signals.append(sub_signals["vwap"]["signal"])
    signals.append(sub_signals["cmf"]["signal"])
    key_findings.append(f"最新收盘价相对VWAP偏离 {vwap_deviation * 100:.2f}%。")
    key_findings.append(f"CMF(20) 为 {cmf_last:.4f}，状态为{cmf_label}。")

    if abs(cmf_last) > 0.5:
        risk_notes.append("CMF 出现极端值，需人工确认是否存在异常成交或数据口径问题。")
        needs_review = True
    if abs(vwap_deviation) > 0.05:
        risk_notes.append("收盘价相对 VWAP 偏离超过 5%，存在短期过热或超跌风险。")
        needs_review = True

    if risk_notes:
        risk_level = "high"
    elif needs_review or bullish_count == bearish_count == 2:
        risk_level = "medium"
    else:
        risk_level = "low"

    confidence = 0.45 + abs(score) * 0.1
    if max(bullish_count, bearish_count) >= 3:
        confidence += 0.1
    if needs_review:
        confidence -= 0.1
    confidence = min(0.95, max(0.25, confidence))

    period = f"{dates[0]} 至 {dates[-1]}" if dates[0] or dates[-1] else f"{len(rows)} rows"
    reasoning = (
        f"基于 {len(rows)} 条OHLCV数据计算 OBV、A/D Line、VWAP、CMF；"
        f"当前 {bullish_count} 个指标偏多、{bearish_count} 个指标偏空，综合判断为 {direction}。"
    )

    evidence_date = dates[-1] if dates else ""
    evidence = [
        _evidence(source_name, evidence_date, "close", last_close, "latest", "最新收盘价"),
        _evidence(source_name, evidence_date, "volume", last_volume, "latest", "最新成交量"),
        _evidence(source_name, evidence_date, "OBV", last_obv, f"20d slope={obv_slope:.2f}", sub_signals["obv"]["signal"]),
        _evidence(source_name, evidence_date, "A/D Line", last_adl, f"20d slope={adl_slope:.2f}", sub_signals["ad_line"]["signal"]),
        _evidence(source_name, evidence_date, "VWAP", last_vwap, f"deviation={vwap_deviation * 100:.2f}%", sub_signals["vwap"]["signal"]),
        _evidence(source_name, evidence_date, "CMF(20)", cmf_last, cmf_label, sub_signals["cmf"]["signal"]),
    ]

    return {
        "direction": direction,
        "confidence": _round(confidence, 4),
        "reasoning": reasoning,
        "signals": signals,
        "source": SKILL_NAME,
        "signal_type": "technical",
        "stock_code": stock_code,
        "weight": 1.0,
        "meta": {
            "output_version": "0.1",
            "skill_name": SKILL_NAME,
            "owner_group": OWNER_GROUP,
            "target": target or stock_code,
            "period": period,
            "time_horizon": "mid",
            "risk_level": risk_level,
            "key_findings": key_findings,
            "evidence": evidence,
            "risk_notes": risk_notes,
            "uncertainties": uncertainties,
            "needs_human_review": needs_review,
            "sub_signals": sub_signals,
            "divergence_detected": {
                "bearish_divergence": False,
                "bullish_divergence": False,
                "involved_indicators": [],
                "divergence_span_days": 0,
            },
        },
    }


def _evidence(source_name, date, metric, value, comparison, note):
    return {
        "source_type": "market_data",
        "source_name": source_name,
        "date": date,
        "metric": metric,
        "value": "" if value is None else str(_round(value, 4)),
        "comparison": comparison,
        "note": note,
    }


def _neutral_signal(stock_code, target, source_name, uncertainty):
    return {
        "direction": "neutral",
        "confidence": 0.25,
        "reasoning": "必填行情数据不足，无法形成可靠量价判断。",
        "signals": ["数据不足"],
        "source": SKILL_NAME,
        "signal_type": "technical",
        "stock_code": stock_code,
        "weight": 1.0,
        "meta": {
            "output_version": "0.1",
            "skill_name": SKILL_NAME,
            "owner_group": OWNER_GROUP,
            "target": target or stock_code,
            "period": "",
            "time_horizon": "mid",
            "risk_level": "high",
            "key_findings": ["OHLCV 数据不足。"],
            "evidence": [],
            "risk_notes": ["数据不足导致结论不可用。"],
            "uncertainties": [uncertainty],
            "needs_human_review": True,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze OHLCV data with volume-price momentum indicators.")
    parser.add_argument("csv_path", help="CSV file with date, high, low, close, volume columns.")
    parser.add_argument("--stock-code", default="", help="Optional stock/index/ETF code.")
    parser.add_argument("--target", default="", help="Optional target display name.")
    args = parser.parse_args()

    rows = load_ohlcv_csv(args.csv_path)
    result = analyze(
        rows,
        stock_code=args.stock_code,
        target=args.target,
        source_name=Path(args.csv_path).name,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
