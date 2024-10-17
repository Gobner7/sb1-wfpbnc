import numpy as np
import pandas as pd
from backtesting import Strategy
from src.indicators.custom_indicators import (
    calculate_atr, calculate_supertrend, calculate_vwap,
    calculate_volume_profile, identify_support_resistance
)

class AdvancedBreakoutStrategy(Strategy):
    n_atr = 14
    n_supertrend = 10
    atr_multiplier = 3
    volume_threshold = 1.5
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    breakout_threshold = 1.5

    def init(self):
        self.atr = self.I(calculate_atr, self.data.high, self.data.low, self.data.close, self.n_atr)
        self.supertrend = self.I(calculate_supertrend, self.data.high, self.data.low, self.data.close, self.n_supertrend, self.atr_multiplier)
        self.vwap = self.I(calculate_vwap, self.data.high, self.data.low, self.data.close, self.data.volume)
        self.volume_profile = self.I(calculate_volume_profile, self.data.close, self.data.volume)
        self.support, self.resistance = self.I(identify_support_resistance, self.data.high, self.data.low, self.data.close)
        
        self.rsi = self.I(lambda: pd.Series(self.data.ta.rsi(length=self.rsi_period)))
        macd_data = self.data.ta.macd(fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal)
        self.macd = self.I(lambda: macd_data['MACD_' + str(self.macd_fast) + '_' + str(self.macd_slow) + '_' + str(self.macd_signal)])
        self.macd_signal = self.I(lambda: macd_data['MACDs_' + str(self.macd_fast) + '_' + str(self.macd_slow) + '_' + str(self.macd_signal)])
        
        self.volume_sma = self.I(lambda: pd.Series(self.data.volume).rolling(20).mean())

    def next(self):
        # Trend analysis
        trend = 1 if self.supertrend[-1] < self.data.close[-1] else -1

        # Volume confirmation
        volume_confirmed = self.data.volume[-1] > self.volume_sma[-1] * self.volume_threshold

        # Breakout detection
        breakout_up = (self.data.close[-1] > self.resistance[-1] * self.breakout_threshold) and (self.data.close[-2] <= self.resistance[-2])
        breakout_down = (self.data.close[-1] < self.support[-1] / self.breakout_threshold) and (self.data.close[-2] >= self.support[-2])

        # RSI conditions
        rsi_buy_condition = self.rsi[-1] < self.rsi_oversold
        rsi_sell_condition = self.rsi[-1] > self.rsi_overbought

        # MACD conditions
        macd_buy_condition = self.macd[-1] > self.macd_signal[-1] and self.macd[-2] <= self.macd_signal[-2]
        macd_sell_condition = self.macd[-1] < self.macd_signal[-1] and self.macd[-2] >= self.macd_signal[-2]

        # Entry conditions
        long_condition = trend == 1 and breakout_up and volume_confirmed and rsi_buy_condition and macd_buy_condition
        short_condition = trend == -1 and breakout_down and volume_confirmed and rsi_sell_condition and macd_sell_condition

        # Position sizing
        risk_per_trade = 0.02  # 2% risk per trade
        stop_loss_pips = self.atr[-1] * self.atr_multiplier
        position_size = self.position_size_calculator(risk_per_trade, stop_loss_pips)

        # Execute trades
        if not self.position:
            if long_condition:
                self.buy(size=position_size, sl=self.data.close[-1] - stop_loss_pips)
            elif short_condition:
                self.sell(size=position_size, sl=self.data.close[-1] + stop_loss_pips)
        
        # Exit conditions
        elif self.position.is_long:
            if trend == -1 or (breakout_down and rsi_sell_condition):
                self.position.close()
        elif self.position.is_short:
            if trend == 1 or (breakout_up and rsi_buy_condition):
                self.position.close()

    def position_size_calculator(self, risk_per_trade, stop_loss_pips):
        account_balance = self.equity
        position_size = (account_balance * risk_per_trade) / stop_loss_pips
        return position_size

    def update_params(self, params):
        for key, value in params.items():
            setattr(self, key, value)