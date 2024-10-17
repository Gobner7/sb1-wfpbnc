import asyncio
import aiohttp
from datetime import datetime, timedelta
import pandas as pd

class DataFetcher:
    def __init__(self, symbol, timeframe, total_limit):
        self.symbol = symbol
        self.timeframe = timeframe
        self.total_limit = total_limit
        self.base_url = 'https://api.hyperliquid.xyz/info'

    async def fetch_data(self):
        async with aiohttp.ClientSession() as session:
            all_data = []
            end_time = datetime.now()
            start_time = end_time - timedelta(days=self.total_limit)

            while start_time < end_time:
                chunk_end = min(start_time + timedelta(days=1), end_time)
                data = await self._fetch_chunk(session, start_time, chunk_end)
                all_data.extend(data)
                start_time = chunk_end

            return pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    async def _fetch_chunk(self, session, start_time, end_time):
        payload = {
            "type": "candleSnapshot",
            "req": {
                "coin": self.symbol,
                "interval": self.timeframe,
                "startTime": int(start_time.timestamp() * 1000),
                "endTime": int(end_time.timestamp() * 1000)
            }
        }

        async with session.post(self.base_url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return [
                    [
                        datetime.fromtimestamp(candle['t'] / 1000),
                        float(candle['o']),
                        float(candle['h']),
                        float(candle['l']),
                        float(candle['c']),
                        float(candle['v'])
                    ]
                    for candle in data
                ]
            else:
                print(f"Error fetching data: {response.status}")
                return []

    async def fetch_live_data(self):
        # Implement WebSocket connection for live data
        pass