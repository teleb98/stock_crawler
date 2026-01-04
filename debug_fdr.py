import FinanceDataReader as fdr

print("Attempting to fetch KRX...")
try:
    df = fdr.StockListing('KRX')
    print(f"KRX Success: {len(df)}")
except Exception as e:
    print(f"KRX Failed: {e}")

print("Attempting to fetch KOSPI...")
try:
    df = fdr.StockListing('KOSPI')
    print(f"KOSPI Success: {len(df)}")
except Exception as e:
    print(f"KOSPI Failed: {e}")
