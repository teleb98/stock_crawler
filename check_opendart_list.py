import OpenDartReader
import pandas as pd

api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
dart = OpenDartReader(api_key)

print("Inspecting Corp Codes...")
# Access the internal dataframe if possible or re-fetch
# The library usually loads it into dart.params['corp_codes'] but let's check attributes
# Or use dart.corp_codes property if it exists
try:
    # It might be a method in some versions or property
    # Attempting to see what `dart` has
    print(dir(dart))
    
    # Standard OpenDartReader stores it in self.corp_codes (DataFrame)
    if hasattr(dart, 'corp_codes'):
        df = dart.corp_codes
        print(df.columns)
        print(df.head())
        print(f"Unique corp_cls: {df['corp_cls'].unique() if 'corp_cls' in df.columns else 'Not found'}")
    else:
        print("dart.corp_codes not found")

except Exception as e:
    print(f"Error: {e}")
