import numpy as np
import pandas as pd

def calculate_atr(high, low, close, period):
    return pd.Series(close).ta.atr(high=high, low=low, length=period)

def calculate_supertrend(high, low, close, period, multiplier):
    return pd.Series(close).ta.supertrend(high=high, low=low, length=period, multiplier=multiplier)[f'SUPERT_{period}_{multiplier}']

def calculate_vwap(high, low, close, volume):
    typical_price = (high + low + close) / 3
    return (typical_price * volume).cumsum() / volume.cumsum()

def calculate_volume_profile(close, volume, bins=10):
    price_range = np.linspace(close.min(), close.max(), bins)
    volume_profile = np.histogram(close, bins=price_range, weights=volume)[0]
    return pd.Series(volume_profile, index=price_range[:-1])

def identify_support_resistance(high, low, close, window=14):
    pivot_high = high.rolling(window=window, center=True).max()
    pivot_low = low.rolling(window=window, center=True).min()
    
    support = pivot_low.where((pivot_low.shift(1) > pivot_low) & (pivot_low.shift(-1) > pivot_low))
    resistance = pivot_high.where((pivot_high.shift(1) < pivot_high) & (pivot_high.shift(-1) < pivot_high))
    
    return support, resistance

def calculate_zigzag(high, low, deviation=5):
    zigzag = pd.Series(index=high.index, dtype=float)
    deviation /= 100
    
    last_high, last_low = high.iloc[0], low.iloc[0]
    last_high_index, last_low_index = 0, 0
    trend = None
    
    for i in range(1, len(high)):
        if trend is None or trend == 1:
            if low[i] < last_low * (1 - deviation):
                if trend == 1:
                    zigzag[last_high_index] = last_high
                trend = -1
                last_low = low[i]
                last_low_index = i
            elif high[i] > last_high:
                last_high = high[i]
                last_high_index = i
        else:
            if high[i] > last_high * (1 + deviation):
                zigzag[last_low_index] = last_low
                trend = 1
                last_high = high[i]
                last_high_index = i
            elif low[i] < last_low:
                last_low = low[i]
                last_low_index = i
    
    if trend == 1:
        zigzag[last_high_index] = last_high
    elif trend == -1:
        zigzag[last_low_index] = last_low
    
    return zigzag

def calculate_ichimoku(high, low, close):
    tenkan_window = 9
    kijun_window = 26
    senkou_span_b_window = 52
    
    tenkan_sen = (high.rolling(window=tenkan_window).max() + low.rolling(window=tenkan_window).min()) / 2
    kijun_sen = (high.rolling(window=kijun_window).max() + low.rolling(window=kijun_window).min()) / 2
    senkou_span_a = (tenkan_sen + kijun_sen) / 2
    senkou_span_b = (high.rolling(window=senkou_span_b_window).max() + low.rolling(window=senkou_span_b_window).min()) / 2
    chikou_span = close.shift(-kijun_window)
    
    return pd.DataFrame({
        'Tenkan Sen': tenkan_sen,
        'Kijun Sen': kijun_sen,
        'Senkou Span A': senkou_span_a,
        'Senkou Span B': senkou_span_b,
        'Chikou Span': chikou_span
    })