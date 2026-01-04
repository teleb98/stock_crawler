from pykrx import stock
from datetime import datetime

# Adjust date to a likely business day (Friday Jan 2, 2026)
date = "20260102"
print(f"Fetching tickers for {date}...")

try:
    tickers_kospi = stock.get_market_ticker_list(date, market="KOSPI")
    print(f"KOSPI Tickers: {len(tickers_kospi)}")
    print(f"Sample: {tickers_kospi[:3]}")
    
    tickers_kosdaq = stock.get_market_ticker_list(date, market="KOSDAQ")
    print(f"KOSDAQ Tickers: {len(tickers_kosdaq)}")
except Exception as e:
    print(f"Error: {e}")
