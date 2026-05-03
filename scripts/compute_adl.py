import numpy as np

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
