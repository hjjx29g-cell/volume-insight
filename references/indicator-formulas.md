# 四个量能指标统一公式手册

## OBV
OBV_t = OBV_{t-1} + (Volume_t if Close_t > Close_{t-1} else -Volume_t if Close_t < Close_{t-1} else 0)

## A/D Line
MFM_t = ( (Close_t - Low_t) - (High_t - Close_t) ) / (High_t - Low_t)   # 若 High==Low 则 MFM = Close_t/Close_{t-1} - 1  
MFV_t = MFM_t × Volume_t  
ADL_t = ADL_{t-1} + MFV_t

## CMF (20-day)
CMF_t = sum_{i=t-19}^{t} MFV_i / sum_{i=t-19}^{t} Volume_i

## VWAP (cumulative over interval, per bar)
TypicalPrice_i = (High_i + Low_i + Close_i) / 3  
VWAP_t = sum_{i=0..t}( TypicalPrice_i × Volume_i ) / sum_{i=0..t}( Volume_i )  
（脚本 `scripts/compute_vwap.py` 输出与 K 线等长的序列；最后一根即全区间 VWAP。）
