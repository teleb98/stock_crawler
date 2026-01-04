from pykrx import stock
import pandas as pd
import traceback

def verify_fetch():
    date = "20260102" 
    print(f"Testing fetch for {date}...")

    try:
        print("Fetching OHLCV...")
        df_price = stock.get_market_ohlcv_by_ticker(date, market="ALL")
        print(f"OHLCV Columns: {df_price.columns.tolist()}")
        print(f"OHLCV Shape: {df_price.shape}")
    except Exception:
        traceback.print_exc()

    try:
        print("Fetching Fundamentals...")
        df_fund = stock.get_market_fundamental_by_ticker(date, market="ALL")
        print(f"Fund Columns: {df_fund.columns.tolist()}")
        print(f"Fund Shape: {df_fund.shape}")
    except Exception:
        print("Error fetching fundamentals:")
        traceback.print_exc()

    try:
        print("Fetching Market Cap...")
        df_cap = stock.get_market_cap_by_ticker(date, market="ALL")
        print(f"Cap Columns: {df_cap.columns.tolist()}")
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    verify_fetch()
