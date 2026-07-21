import pandas as pd
import yfinance as yf
import numpy as np

#Download apple data from Jan 1 2020 to Jan 1 2024
raw_data = yf.download("AAPL", start="2020-01-01", end="2024-01-01")

#Clean df with just close price
df = pd.DataFrame()
df['Close'] = raw_data['Close']['AAPL']

#Calculate moving averages
df['SMA50'] = df['Close'].rolling(window=50).mean()
df['SMA200'] = df['Close'].rolling(window=200).mean()

#use dropna to delete rows with missing data and copy for safety
df_clean = df.dropna().copy()

#Vectorized if/else statement
#Buy if sma50 > sm200
df_clean['Signal'] = np.where(df_clean['SMA50'] > df_clean['SMA200'], 1, -1)
df_clean['MarketReturn'] = df_clean['Close'].pct_change()

#calculate strategy by shifting signal down one row and multiplying (1 mean hold and -1 mean sell)
df_clean['StrategyReturn'] = df_clean['Signal'].shift(1) * df_clean['MarketReturn']

#Calculate compound growth (+1 to return (5% return becomes 1.05) before compounding)
df_clean['CumulativeReturn'] = (1 + df_clean['StrategyReturn']).cumprod()

#Calculate cumulative return of just holding the stock
df_clean['MarketCumulative'] = (1 + df_clean['MarketReturn']).cumprod()

print(df_clean[['Close', 'Signal', 'StrategyReturn', 'CumulativeReturn']].tail())
print("\n ---Final Result---")
print(df_clean[['MarketCumulative', 'CumulativeReturn']].tail(1))