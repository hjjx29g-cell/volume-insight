# 标准 Signal JSON 输出示例

```json
{
  "direction": "bullish",
  "confidence": 0.85,
  "reasoning": "基于 9 条OHLCV数据计算 OBV、A/D Line、VWAP、CMF；当前 3 个指标偏多、0 个指标偏空，综合判断为 bullish。",
  "signals": [
    "多指标共振偏多",
    "价格站上VWAP",
    "CMF中性"
  ],
  "source": "volume_price_momentum_analysis",
  "signal_type": "technical",
  "stock_code": "TEST",
  "weight": 1.0,
  "meta": {
    "output_version": "0.1",
    "skill_name": "volume_price_momentum_analysis",
    "owner_group": "专家2组（指标）",
    "target": "示例公司",
    "period": "2025-01-02 至 2025-01-10",
    "time_horizon": "mid",
    "risk_level": "low",
    "key_findings": [
      "OBV、A/D、VWAP、CMF 中至少 3 个指标偏多。",
      "最新收盘价相对VWAP偏离 4.04%。",
      "CMF(20) 为 0.0000，状态为中性。"
    ],
    "evidence": [
      {
        "source_type": "market_data",
        "source_name": "sample_data.csv",
        "date": "2025-01-10",
        "metric": "close",
        "value": "110.0",
        "comparison": "latest",
        "note": "最新收盘价"
      },
      {
        "source_type": "market_data",
        "source_name": "sample_data.csv",
        "date": "2025-01-10",
        "metric": "VWAP",
        "value": "105.7333",
        "comparison": "deviation=4.04%",
        "note": "价格站上VWAP"
      },
      {
        "source_type": "market_data",
        "source_name": "sample_data.csv",
        "date": "2025-01-10",
        "metric": "CMF(20)",
        "value": "0.0",
        "comparison": "中性",
        "note": "CMF中性"
      }
    ],
    "risk_notes": [],
    "uncertainties": [],
    "needs_human_review": false,
    "sub_signals": {
      "obv": {
        "signal": "OBV趋势上升",
        "direction": "bullish",
        "confidence": 0.6,
        "latest_value": 10250000.0,
        "slope_20d": 1278333.33
      },
      "ad_line": {
        "signal": "A/D累积上升",
        "direction": "bullish",
        "confidence": 0.6,
        "latest_value": 3950000.0,
        "slope_20d": 449444.44
      },
      "vwap": {
        "signal": "价格站上VWAP",
        "direction": "bullish",
        "confidence": 0.62,
        "latest_value": 105.7333,
        "price_deviation_pct": 4.04
      },
      "cmf": {
        "signal": "CMF中性",
        "direction": "neutral",
        "confidence": 0.5,
        "latest_value": 0.0,
        "zone": "neutral"
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
