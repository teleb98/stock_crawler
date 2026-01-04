import OpenDartReader
import yfinance as yf
from pykrx import stock

api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"

print("--- Testing OpenDartReader ---")
try:
    dart = OpenDartReader(api_key)
    # Fetch corpse listings. This usually works ?
    # Note: dart.corp_codes causes a download of XML.
    # We'll try to get it.
    corp_codes = dart.corp_codes
    print(f"Dart Corp Codes fetched. Count: {len(corp_codes)}")
    print("Head:", corp_codes.head())
    
    # Check if we can map to stock code
    listed = corp_codes[corp_codes['stock_code'].notnull()]
    print(f"Listed companies: {len(listed)}")
except Exception as e:
    print("OpenDart Failed:", e)

print("\n--- Testing yfinance (Samsung Elec) ---")
try:
    ticker = "005930.KS"
    yf_ticker = yf.Ticker(ticker)
    hist = yf_ticker.history(start="2024-01-02", end="2024-01-06")
    print("YF History:\n", hist)
except Exception as e:
    print("YF Failed:", e)

print("\n--- Testing pykrx PER-TICKER (Samsung Elec) ---")
try:
    # 005930
    df = stock.get_market_fundamental_by_date("20240104", "20240104", "005930")
    print("Pykrx Per-Ticker Fund:\n", df)
except Exception as e:
    print("Pykrx Per-Ticker Failed:", e)
