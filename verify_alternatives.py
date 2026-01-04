import OpenDartReader
import FinanceDataReader as fdr
import pandas as pd

def verify_alternatives():
    api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557" # User provided
    dart = OpenDartReader(api_key)
    
    print("Fetching OpenDart Corp List...")
    try:
        # corp_codes object usually has finding methods
        # To get the dataframe of all corps:
        # It's not directly exposed as a DF in all versions, let's check.
        # usually dart.corp_codes is the XML raw or processed wrapper.
        # But 'dart.list()' is for filings.
        # 'dart.corp_codes' is initialized on init.
        
        # We can look at internal df: dart.corp_codes
        # It contains: corp_code, corp_name, stock_code, modify_date
        
        # Let's verify
        print(f"Corp Codes loaded. Sample:")
        # It might be hidden, let's try to access the pandas df if possible or just search
        # Actually usually it's dart.corp_codes works closer to a dictionary or helper
        # But for bulk list:
        # The library processes the XML from DART.
        
        # Let's try to find Samsung Electronics
        samsung = dart.find_corp_code('005930')
        print(f"Samsung via Code: {samsung}")
        
        # If we can access the full list:
        # The library stores it in `dart.params['corp_codes']`? No.
        
        # Looking at library source (standard OpenDartReader):
        # It downloads corp_code.xml and parses it into self.corp_codes (DataFrame)?
        # No, check if we can get the dataframe.
        # Usually checking `dart.corp_codes` property?
        pass

    except Exception as e:
        print(f"OpenDart Error: {e}")
        
    print("\nTesting FDR Price (Naver source, typically):")
    try:
        # 005930 = Samsung Electronics
        df = fdr.DataReader('005930', '2024-01-01', '2024-01-10')
        print(df.head())
        print("FDR Price Fetch Successful!")
    except Exception as e:
        print(f"FDR Price Error: {e}")

if __name__ == "__main__":
    verify_alternatives()
