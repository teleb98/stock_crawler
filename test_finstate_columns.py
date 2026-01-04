import OpenDartReader
import pandas as pd

api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
dart = OpenDartReader(api_key)

corp_code = '005930' # Samsung
year = '2023'
report_code = '11011' # Annual

print("Fetching 2023 Annual Report for Samsung...")
df = dart.finstate(corp_code, year, reprt_code=report_code)

if df is not None:
    print("Columns:", df.columns)
    # Check for thstrm_amount (Current), frmtrm_amount (Previous), bfefrmtrm_amount (Pre-Prev)
    cols = [c for c in df.columns if 'amount' in c]
    print("Amount columns:", cols)
    
    print("\nFirst row sample:")
    print(df.iloc[0])
