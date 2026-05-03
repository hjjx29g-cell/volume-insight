import numpy as np


def compute_vwap(high, low, close, volume):
    """
    区间内逐根 K 线的累积 VWAP（日线常用：从序列起点到 t 的成交量加权典型价）。
    Typical = (High + Low + Close) / 3
    VWAP[t] = sum_{i=0..t}(TP_i * V_i) / sum_{i=0..t}(V_i)
    """
    typical = (
        np.asarray(high, dtype=float)
        + np.asarray(low, dtype=float)
        + np.asarray(close, dtype=float)
    ) / 3.0
    vol = np.asarray(volume, dtype=float)
    cum_pv = np.cumsum(typical * vol)
    cum_vol = np.cumsum(vol)
    return np.divide(
        cum_pv,
        cum_vol,
        out=np.full_like(cum_pv, np.nan, dtype=float),
        where=cum_vol > 0,
    )
