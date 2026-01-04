from pykrx import stock
import pandas as pd
from datetime import datetime

def verify_fetch():
    # Use a recent known business day
    date = "20260102" 
    print(f"Testing fetch for {date}...")

    try:
        # Fundamental
        df_fund = stock.get_market_fundamental_by_ticker(date, market="ALL")
        print("\n[Fundamental Data Columns]")
        print(df_fund.columns.tolist())
        print(df_fund.head(1))

        # Price
        df_price = stock.get_market_ohlcv_by_ticker(date, market="ALL")
        print("\n[Price Data Columns]")
        print(df_price.columns.tolist())
        print(df_price.head(1))

        # Market Cap (often has Name)
        df_cap = stock.get_market_cap_by_ticker(date, market="ALL")
        print("\n[Market Cap Data Columns]")
        print(df_cap.columns.tolist())
        print(df_cap.head(1))
        
        # Check if we can get ticker list
        tickers = stock.get_market_ticker_list(date, market="ALL")
        print(f"\n[Tickers] Found {len(tickers)} tickers.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_fetch()
