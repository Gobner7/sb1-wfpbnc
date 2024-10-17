# Hyperliquid Trading Bot

This is an advanced trading bot for the Hyperliquid exchange, implementing a sophisticated breakout strategy with genetic algorithm optimization.

## Features

- Historical and live data fetching from Hyperliquid API
- Advanced feature engineering using technical indicators
- Breakout strategy with trend following and volatility adjustment
- Backtesting framework for strategy evaluation
- Genetic algorithm for strategy parameter optimization
- Live trading functionality with risk management

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/hyperliquid-trading-bot.git
   cd hyperliquid-trading-bot
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your API credentials:
   - Copy the `.env.example` file to `.env`
   - Edit the `.env` file and add your Hyperliquid API key and secret

5. Configure the bot:
   - Edit the `config.yaml` file to set your desired trading parameters

## Usage

To run the bot:

```
python main.py
```

This will start the bot, which will:
1. Fetch historical data
2. Perform feature engineering
3. Run a backtest with the initial strategy parameters
4. Optimize the strategy using a genetic algorithm
5. Run a backtest with the optimized parameters
6. Start live trading (if enabled in the configuration)

## Disclaimer

This trading bot is for educational and research purposes only. Use it at your own risk. The authors and contributors are not responsible for any financial losses incurred from using this software.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.