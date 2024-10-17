import numpy as np
import pandas as pd

def calculate_performance_metrics(results):
    returns = results['_equity_curve'].pct_change().dropna()
    
    total_return = (results['_equity_curve'].iloc[-1] / results['_equity_curve'].iloc[0] - 1) * 100
    cagr = (results['_equity_curve'].iloc[-1] / results['_equity_curve'].iloc[0]) ** (252 / len(returns)) - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe_ratio = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
    sortino_ratio = (returns.mean() * 252) / (returns[returns < 0].std() * np.sqrt(252))
    max_drawdown = results['_drawdown'].max()
    calmar_ratio = cagr / max_drawdown
    
    win_rate = results['Win Rate [%]']
    profit_factor = results['Profit Factor']
    
    return pd.Series({
        'Total Return (%)': total_return,
        'CAGR (%)': cagr * 100,
        'Volatility (%)': volatility * 100,
        'Sharpe Ratio': sharpe_ratio,
        'Sortino Ratio': sortino_ratio,
        'Max Drawdown (%)': max_drawdown * 100,
        'Calmar Ratio': calmar_ratio,
        'Win Rate (%)': win_rate,
        'Profit Factor': profit_factor
    })