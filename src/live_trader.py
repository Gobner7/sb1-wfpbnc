import asyncio
import ccxt.async_support as ccxt
from src.utils.logger import get_logger

class LiveTrader:
    def __init__(self, api_key, api_secret):
        self.exchange = ccxt.hyperliquid({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'
            }
        })
        self.logger = get_logger()

    async def start_trading(self, strategy):
        try:
            while True:
                await self.execute_trading_cycle(strategy)
                await asyncio.sleep(60)  # Wait for 1 minute before the next cycle
        except Exception as e:
            self.logger.error(f"Error in live trading: {e}")
        finally:
            await self.exchange.close()

    async def execute_trading_cycle(self, strategy):
        # Fetch latest market data
        ohlcv = await self.exchange.fetch_ohlcv(strategy.symbol, strategy.timeframe, limit=100)
        
        # Update strategy with latest data
        strategy.update_data(ohlcv)
        
        # Get trading signals
        signal = strategy.generate_signal()
        
        if signal == 'buy':
            await self.open_long_position(strategy)
        elif signal == 'sell':
            await self.open_short_position(strategy)
        elif signal == 'close':
            await self.close_positions(strategy)

    async def open_long_position(self, strategy):
        try:
            amount = strategy.calculate_position_size()
            order = await self.exchange.create_market_buy_order(strategy.symbol, amount)
            self.logger.info(f"Opened long position: {order}")
        except Exception as e:
            self.logger.error(f"Error opening long position: {e}")

    async def open_short_position(self, strategy):
        try:
            amount = strategy.calculate_position_size()
            order = await self.exchange.create_market_sell_order(strategy.symbol, amount)
            self.logger.info(f"Opened short position: {order}")
        except Exception as e:
            self.logger.error(f"Error opening short position: {e}")

    async def close_positions(self, strategy):
        try:
            positions = await self.exchange.fetch_positions([strategy.symbol])
            for position in positions:
                if position['side'] == 'long':
                    await self.exchange.create_market_sell_order(strategy.symbol, position['amount'])
                elif position['side'] == 'short':
                    await self.exchange.create_market_buy_order(strategy.symbol, position['amount'])
            self.logger.info("Closed all positions")
        except Exception as e:
            self.logger.error(f"Error closing positions: {e}")

    async def get_account_balance(self):
        try:
            balance = await self.exchange.fetch_balance()
            return balance['total']
        except Exception as e:
            self.logger.error(f"Error fetching account balance: {e}")
            return None