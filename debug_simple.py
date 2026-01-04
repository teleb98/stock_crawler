from pykrx import stock
import FinanceDataReader as fdr

date = "20240104"
print(f"Checking ticker list for {date}...")
tickers = stock.get_market_ticker_list(date)
print(f"Tickers found: {len(tickers)}")
if tickers:
    print("First 5:", tickers[:5])

print("\nChecking FinanceDataReader for KRX listing...")
try:
    df_krx = fdr.StockListing('KRX')
    print("FDR KRX Listing head:")
    print(df_krx.head())
    print("FDR Columns:", df_krx.columns.tolist())
except Exception as e:
    print("FDR failed:", e)
