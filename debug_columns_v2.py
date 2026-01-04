from pykrx import stock

date = "20240104"

print("--- Testing OHLCV (ALL) ---")
try:
    df = stock.get_market_ohlcv_by_ticker(date, market="ALL")
    print("OHLCV Columns:", df.columns.tolist())
    print("OHLCV Success")
except Exception as e:
    print("OHLCV Failed:", e)

print("\n--- Testing Fundamentals (KOSPI) ---")
try:
    df = stock.get_market_fundamental_by_ticker(date, market="KOSPI")
    print("Fund KOSPI Columns:", df.columns.tolist())
    print("Fund KOSPI Success")
except Exception as e:
    print("Fund KOSPI Failed:", e)

print("\n--- Testing Fundamentals (KOSDAQ) ---")
try:
    df = stock.get_market_fundamental_by_ticker(date, market="KOSDAQ")
    print("Fund KOSDAQ Columns:", df.columns.tolist())
    print("Fund KOSDAQ Success")
except Exception as e:
    print("Fund KOSDAQ Failed:", e)
    
print("\n--- Testing Market Cap (ALL) ---")
try:
    df = stock.get_market_cap_by_ticker(date, market="ALL")
    print("Cap Columns:", df.columns.tolist())
    print("Cap Success")
except Exception as e:
    print("Cap Failed:", e)
