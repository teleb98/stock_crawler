import FinanceDataReader as fdr
import pandas as pd

def verify_fdr():
    print("Testing FinanceDataReader...")
    try:
        # Fetch KRX listing (Current)
        df_krx = fdr.StockListing('KRX')
        print(f"KRX Listing Count: {len(df_krx)}")
        print(df_krx.head())
        print(df_krx.columns)
        
        # Fetch Price for one ticker (Samsung Electronics 005930)
        df_price = fdr.DataReader('005930', '2024-01-01', '2024-01-10')
        print("\n[Price Data Sample]")
        print(df_price)
        
    except Exception as e:
        print(f"Error with FDR: {e}")

if __name__ == "__main__":
    verify_fdr()
