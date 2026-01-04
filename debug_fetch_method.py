import OpenDartReader
import pandas as pd

api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
dart = OpenDartReader(api_key)

# Samsung Electronics
target_name = "삼성전자"
target_stock = "005930"
target_corp = "00126380" # From manual check or cache
year = "2023"
report = "11011"

print(f"--- Debugging Fetch for {target_name} ---")

# 1. Test with Stock Code
print(f"\n1. Fetching with Stock Code: {target_stock}")
try:
    df1 = dart.finstate(target_stock, year, reprt_code=report)
    if df1 is not None:
        print(f"   Success! Rows: {len(df1)}")
    else:
        print("   Returned None")
except Exception as e:
    print(f"   Error: {e}")

# 2. Test with Corp Code
print(f"\n2. Fetching with Corp Code: {target_corp}")
try:
    # Note: OpenDartReader might be picky about whether this is a string matching exactly
    df2 = dart.finstate(target_corp, year, reprt_code=report)
    if df2 is not None:
        print(f"   Success! Rows: {len(df2)}")
    else:
        print("   Returned None")
except Exception as e:
    print(f"   Error: {e}")

# 3. Check what's in the cache for Samsung
print("\n3. Checking Cache Data for Samsung")
df_corp = dart.corp_codes
row = df_corp[df_corp['stock_code'] == target_stock]
print(row)
if not row.empty:
    cache_corp = row.iloc[0]['corp_code']
    print(f"   Cache Corp Code: '{cache_corp}'")
    print(f"   Target Corp Code: '{target_corp}'")
    print(f"   Match? {cache_corp == target_corp}")
    
    # 4. Try fetching with the exact value from cache
    print(f"\n4. Fetching with Cache Corp Code extracted directly: '{cache_corp}'")
    try:
        df3 = dart.finstate(cache_corp, year, reprt_code=report)
        if df3 is not None:
            print(f"   Success! Rows: {len(df3)}")
        else:
            print("   Returned None")
    except Exception as e:
        print(f"   Error: {e}")
