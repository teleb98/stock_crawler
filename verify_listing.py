import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd

def verify_listing_and_yf():
    print("Testing FDR Listing (KOSPI)...")
    try:
        # KOSPI might use Naver or KRX
        df_kospi = fdr.StockListing('KOSPI')
        print(f"KOSPI count: {len(df_kospi)}")
        print(df_kospi.head())
        print(df_kospi.columns)
    except Exception as e:
        print(f"FDR KOSPI Error: {e}")

    print("\nTesting YFinance for Samsung (005930.KS)...")
    try:
        # yfinance often works
        ticker = yf.Ticker("005930.KS")
        hist = ticker.history(period="1mo")
        print(f"YF History:\n{hist.head(2)}")
        
        # Check if YF has info (current fundamentals)
        info = ticker.info
        print(f"YF Info Keys: {list(info.keys())[:10]}")
        print(f"PBR: {info.get('priceToBook')}, PER: {info.get('trailingPE')}")
        
    except Exception as e:
        print(f"YFinance Error: {e}")

if __name__ == "__main__":
    verify_listing_and_yf()
