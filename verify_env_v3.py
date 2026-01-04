from pykrx import stock
import pandas as pd
import traceback

def verify_fetch():
    dates = ["20240104", "20250102", "20260102"] 
    
    for date in dates:
        print(f"\n--- Testing fetch for {date} ---")
        try:
            tickers = stock.get_market_ticker_list(date)
            print(f"Tickers found: {len(tickers)}")
            
            if len(tickers) > 0:
                print("Fetching OHLCV (first ticker)...")
                # Try fetching single ticker first to see if that works
                single_ticker = tickers[0]
                df_single = stock.get_market_ohlcv(date, date, single_ticker)
                print(f"Single ticker {single_ticker} OHLCV:\n{df_single}")
                
                print("Fetching Market OHLCV (Bulk)...")
                df_price = stock.get_market_ohlcv_by_ticker(date, market="ALL")
                print(f"Bulk OHLCV Shape: {df_price.shape}")
            else:
                print("No tickers found. Market might be closed or API broken.")

        except Exception as e:
            print(f"Error fetching {date}: {e}")
            # traceback.print_exc()

if __name__ == "__main__":
    verify_fetch()
