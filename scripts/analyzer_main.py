import pandas as pd
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
