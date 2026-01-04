import OpenDartReader
import pandas as pd

api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
dart = OpenDartReader(api_key)

print("Testing finstate_all for Samsung Electronics (005930)...")
try:
    # Try with corp_code
    df = dart.finstate_all('005930', '2023', '11011')
    if df is not None:
        print(f"Result with corp_code: {len(df)} rows")
        print(df.head())
    else:
        print("Result with corp_code is None")
except Exception as e:
    print(f"Error with corp_code: {e}")

print("\nTesting finstate_all WITHOUT corp_code (Bulk mode?)...")
try:
    # Try without corp_code - this might fail if it demands a positional arg
    # Assuming the signature might be (corp_code, year, report_code) or similar
    # If it's a bulk download, maybe it's a different method name or arguments?
    # Let's try passing just year and code? BUT signature likely binds first arg to corp_code if purely positional.
    # So I will try keyword args if possible, or inspection showed arguments? No.
    pass 
    # OpenDartReader usually is wrapper.
    # The API 'fnlttSinglAcntAll' implies 'Single Account (Entire)'? No.
    # Actually there is no 'All Companies' JSON API in OpenDart for financial statements usually. 
    # There IS a bulk file download. 'download_stock_prices'? No.
    
    # Let's try passing year as first arg? Unlikely.
    # I'll enable this block if I suspected it.
except Exception as e:
    print(f"Error without corp_code: {e}")
