import asyncio
import pandas as pd
from dotenv import load_dotenv
from src.data_fetcher import DataFetcher
from src.feature_engineering import FeatureEngineer
from src.strategies.advanced_breakout_strategy import AdvancedBreakoutStrategy
from src.backtester import AdvancedBacktester
from src.genetic_optimizer import GeneticOptimizer
from src.live_trader import LiveTrader
from src.utils.logger import setup_logger
from src.utils.config import load_config

async def main():
    # Load environment variables and configuration
    load_dotenv()
    config = load_config()
    logger = setup_logger()

    # Initialize components
    data_fetcher = DataFetcher(config['symbol'], config['timeframe'], config['total_limit'])
    feature_engineer = FeatureEngineer()
    strategy = AdvancedBreakoutStrategy
    backtester = AdvancedBacktester(pd.DataFrame(), strategy)  # Initialize with empty DataFrame
    genetic_optimizer = GeneticOptimizer(strategy, backtester)
    live_trader = LiveTrader(config['api_key'], config['api_secret'])

    # Fetch and process historical data
    logger.info("Fetching historical data...")
    historical_data = await data_fetcher.fetch_data()
    
    logger.info("Engineering features...")
    engineered_data = feature_engineer.calculate_features(historical_data)

    # Update backtester with engineered data
    backtester.data = engineered_data

    # Run initial backtest
    logger.info("Running initial backtest...")
    initial_results = backtester.run()
    logger.info(f"Initial backtest results:\n{backtester.analyze_results(initial_results)}")

    # Optimize strategy using genetic algorithm
    logger.info("Optimizing strategy...")
    optimization_params = {
        'n_atr': range(10, 30),
        'n_supertrend': range(5, 20),
        'atr_multiplier': range(1, 5),
        'volume_threshold': range(10, 30, 5),  # 1.0 to 3.0 step 0.5
        'rsi_period': range(10, 30),
        'rsi_overbought': range(65, 85, 5),
        'rsi_oversold': range(15, 35, 5),
        'macd_fast': range(8, 20),
        'macd_slow': range(20, 40),
        'macd_signal': range(5, 15),
        'breakout_threshold': range(10, 30, 5)  # 1.0 to 3.0 step 0.5
    }
    optimized_params = genetic_optimizer.optimize(engineered_data, optimization_params)
    strategy.update_params(optimized_params)

    # Run backtest with optimized strategy
    logger.info("Running backtest with optimized strategy...")
    optimized_results = backtester.run()
    logger.info(f"Optimized backtest results:\n{backtester.analyze_results(optimized_results)}")

    # Run Monte Carlo simulation
    logger.info("Running Monte Carlo simulation...")
    monte_carlo_results = backtester.run_monte_carlo()

    # Generate and print full report
    report = backtester.generate_report(optimized_results, optimized_params, monte_carlo_results)
    logger.info(f"Full Backtesting Report:\n{report}")

    # Start live trading if enabled
    if config['live_trading_enabled']:
        logger.info("Starting live trading...")
        await live_trader.start_trading(strategy)
    else:
        logger.info("Live trading is disabled. Exiting...")

if __name__ == "__main__":
    asyncio.run(main())