import numpy as np
from backtesting import Strategy

class BreakoutStrategy(Strategy):
    n_sma_fast = 20
    n_sma_slow = 50
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30
    atr_multiplier = 2
    volume_ratio_threshold = 1.5

    def init(self):
        self.sma_fast = self.I(lambda: self.data.sma_fast)
        self.sma_slow = self.I(lambda: self.data.sma_slow)
        self.rsi = self.I(lambda: self.data.rsi)
        self.atr = self.I(lambda: self.data.atr)
        self.volume_ratio = self.I(lambda: self.data.volume / self.data.volume.rolling(20).mean())

    def next(self):
        # Trend following
        trend = 1 if self.sma_fast[-1] > self.sma_slow[-1] else -1

        # Volatility adjustment
        volatility_factor = self.atr[-1] / self.data.close[-1]

        # Volume confirmation
        volume_confirmed = self.volume_ratio[-1] > self.volume_ratio_threshold

        # RSI conditions
        rsi_buy_condition = self.rsi[-1] < self.rsi_oversold
        rsi_sell_condition = self.rsi[-1] > self.rsi_overbought

        # Breakout conditions
        breakout_buy = self.data.close[-1] > self.data.resistance[-1]
        breakout_sell = self.data.close[-1] < self.data.support[-1]

        # Entry conditions
        if not self.position:
            if trend == 1 and breakout_buy and rsi_buy_condition and volume_confirmed:
                self.buy(size=self.calculate_position_size(), sl=self.data.close[-1] - self.atr[-1] * self.atr_multiplier)
            elif trend == -1 and breakout_sell and rsi_sell_condition and volume_confirmed:
                self.sell(size=self.calculate_position_size(), sl=self.data.close[-1] + self.atr[-1] * self.atr_multiplier)

        # Exit conditions
        elif self.position.is_long:
            if trend == -1 or (breakout_sell and rsi_sell_condition):
                self.position.close()
        elif self.position.is_short:
            if trend == 1 or (breakout_buy and rsi_buy_condition):
                self.position.close()

    def calculate_position_size(self):
        # Implement position sizing based on account balance, risk per trade, and current volatility
        account_balance = self.equity
        risk_per_trade = 0.02  # 2% risk per trade
        volatility = self.atr[-1]
        
        position_size = (account_balance * risk_per_trade) / volatility
        return position_size

    def update_params(self, params):
        for key, value in params.items():
            setattr(self, key, value)