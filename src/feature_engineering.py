import pandas as pd
import numpy as np
import talib

class FeatureEngineer:
    def calculate_features(self, df):
        # Technical indicators
        df['sma_fast'] = talib.SMA(df['close'], timeperiod=20)
        df['sma_slow'] = talib.SMA(df['close'], timeperiod=50)
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        df['macd'], df['macd_signal'], _ = talib.MACD(df['close'])
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'] = talib.BBANDS(df['close'])

        # Volume indicators
        df['obv'] = talib.OBV(df['close'], df['volume'])
        df['adosc'] = talib.ADOSC(df['high'], df['low'], df['close'], df['volume'])

        # Momentum indicators
        df['mom'] = talib.MOM(df['close'], timeperiod=10)
        df['roc'] = talib.ROC(df['close'], timeperiod=10)

        # Volatility
        df['volatility'] = df['close'].rolling(window=20).std()

        # Custom features
        df['price_change'] = df['close'].pct_change()
        df['volume_change'] = df['volume'].pct_change()
        df['high_low_range'] = (df['high'] - df['low']) / df['low']

        # Market regime
        df['market_regime'] = np.where(df['sma_fast'] > df['sma_slow'], 1, -1)

        # Support and resistance levels
        df['support'] = df['low'].rolling(window=20).min()
        df['resistance'] = df['high'].rolling(window=20).max()

        # Candlestick patterns
        df['doji'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
        df['engulfing'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
        df['hammer'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])

        # Time-based features
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

        return df

    def normalize_features(self, df):
        # Normalize numerical features
        numerical_features = ['sma_fast', 'sma_slow', 'rsi', 'macd', 'atr', 'obv', 'adosc', 'mom', 'roc', 'volatility']
        df[numerical_features] = (df[numerical_features] - df[numerical_features].mean()) / df[numerical_features].std()
        return df