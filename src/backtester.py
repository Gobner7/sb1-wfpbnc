from backtesting import Backtest
import pandas as pd
import matplotlib.pyplot as plt
from src.utils.performance_metrics import calculate_performance_metrics

class AdvancedBacktester:
    def __init__(self, data, strategy, cash=10000, commission=0.002):
        self.data = data
        self.strategy = strategy
        self.cash = cash
        self.commission = commission

    def run(self, **kwargs):
        bt = Backtest(self.data, self.strategy, cash=self.cash, commission=self.commission, exclusive_orders=True)
        results = bt.run(**kwargs)
        return results

    def optimize(self, optimization_params, maximize='Sharpe Ratio'):
        bt = Backtest(self.data, self.strategy, cash=self.cash, commission=self.commission, exclusive_orders=True)
        optimized_results = bt.optimize(**optimization_params, maximize=maximize)
        return optimized_results

    def run_monte_carlo(self, num_simulations=1000):
        results = []
        for _ in range(num_simulations):
            shuffled_data = self.data.sample(frac=1).reset_index(drop=True)
            bt = Backtest(shuffled_data, self.strategy, cash=self.cash, commission=self.commission, exclusive_orders=True)
            result = bt.run()
            results.append(result['Return [%]'])
        return pd.Series(results)

    def analyze_results(self, results):
        performance_metrics = calculate_performance_metrics(results)
        self.plot_equity_curve(results)
        self.plot_drawdown(results)
        return performance_metrics

    def plot_equity_curve(self, results):
        plt.figure(figsize=(12, 6))
        plt.plot(results['_equity_curve'])
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Equity')
        plt.show()

    def plot_drawdown(self, results):
        plt.figure(figsize=(12, 6))
        plt.plot(results['_drawdown'])
        plt.title('Drawdown')
        plt.xlabel('Date')
        plt.ylabel('Drawdown %')
        plt.show()

    def generate_report(self, results, optimized_results=None, monte_carlo_results=None):
        report = f"""
        Backtesting Report
        ------------------
        Initial Capital: ${self.cash}
        Commission: {self.commission * 100}%

        Performance Metrics:
        {self.analyze_results(results)}

        Trade Statistics:
        Total Trades: {results['# Trades']}
        Win Rate: {results['Win Rate [%]']:.2f}%
        Profit Factor: {results['Profit Factor']:.2f}
        Sharpe Ratio: {results['Sharpe Ratio']:.2f}
        Sortino Ratio: {results['Sortino Ratio']:.2f}
        Max Drawdown: {results['Max. Drawdown [%]']:.2f}%
        """

        if optimized_results is not None:
            report += f"""
            Optimization Results:
            Best Parameters: {optimized_results['_strategy']}
            Best Performance: {optimized_results['_equity_final']}
            """

        if monte_carlo_results is not None:
            report += f"""
            Monte Carlo Simulation Results:
            Mean Return: {monte_carlo_results.mean():.2f}%
            Median Return: {monte_carlo_results.median():.2f}%
            5th Percentile: {monte_carlo_results.quantile(0.05):.2f}%
            95th Percentile: {monte_carlo_results.quantile(0.95):.2f}%
            """

        return report