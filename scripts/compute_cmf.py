import numpy as np

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
