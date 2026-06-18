import pandas as pd
import numpy as np

def sma_backtest(csv_path):
    print(f"Loading data from {csv_path}...")
    
    #Load and prep the data
    try:
        df = pd.read_csv(csv_path, parse_dates=['Date'], index_col='Date')
    except FileNotFoundError:
        print(f"Error: Could not find {csv_path}")
        return
    
    #Sort indexes by date in chronological order
    df = df.sort_index()
    
    price_col = 'Adj Close'
    if price_col not in df.columns:
        print("Warning: 'Adj Close' not found, falling back to 'Close'. Results may be skewed by splits.")
        price_col = 'Close'
    
    #Calculate the daily market return (% change from yesterday to today)
    df['market_return'] = df['Close'].pct_change()
    
    #Calculate the moving averages
    fast_window = 10
    slow_window = 50
    
    df['fast_ma'] = df['Close'].rolling(window=10).mean()
    df['slow_ma'] = df['Close'].rolling(window=50).mean()
    df = df.dropna(subset=['slow_ma'])
    df['signal'] = np.where(df['fast_ma'] > df['slow_ma'], 1, 0)
    
    #Calculate signal change
    df['trades'] = df['signal'].diff().abs() 
    transaction_cost_pct = 0.001 
    
    #Prevent lookahead bias
    df['strategy_return'] = (df['signal'].shift(1) * df['market_return']) - (df['trades'] * transaction_cost_pct)
    df = df.dropna(subset=['strategy_return'])
    
    #Cumulative return
    df['cumulative_market'] = (1 + df['market_return']).cumprod() - 1
    df['cumulative_strategy'] = (1 + df['strategy_return']).cumprod() - 1

    running_max = (1 + df['cumulative_strategy']).cummax()
    # Calculate how far we have dropped from the running maximum
    drawdown = ((1 + df['cumulative_strategy']) - running_max) / running_max
    max_drawdown = drawdown.min() * 100

    #Return results
    total_market_return = df['cumulative_market'].iloc[-1] * 100
    total_strategy_return = df['cumulative_strategy'].iloc[-1] * 100
    total_trades = df['trades'].sum()

    print("-" * 40)
    print("ADVANCED BACKTEST RESULTS")
    print("-" * 40)
    print(f"Total Trades Executed:   {int(total_trades)}")
    print(f"Total Market Return:     {total_market_return:.2f}%")
    print(f"Total Strategy Return:   {total_strategy_return:.2f}%")
    print(f"Maximum Drawdown:        {max_drawdown:.2f}%")
    print("-" * 40)

if __name__ == "__main__":
    sma_backtest('AAPL.csv')