import OpenDartReader

api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
dart = OpenDartReader(api_key)

print("Fetching company list...")
# corp_codes is usually a DataFrame inside the object
try:
    print(f"Total companies in cache: {len(dart.corp_codes)}")
    
    # Filter for listed companies (stock_code is not None)

    
    # Inspect the type and content properly
    print(f"Type of corp_codes: {type(dart.corp_codes)}")
    
    if hasattr(dart.corp_codes, 'shape'):
        print(f"Shape: {dart.corp_codes.shape}")
        # dart.corp_codes is likely a DataFrame with columns like 'corp_code', 'corp_name', 'stock_code', 'modify_date'
        print("Columns:", dart.corp_codes.columns)
        
        # Filter where stock_code is not empty/None
        # Note: stock_code might be string 'nan' or actual None or empty string.
        # Let's clean it up.
        df = dart.corp_codes
        
        # Filter for non-null and non-empty
        listed = df[df['stock_code'].notna() & (df['stock_code'] != '')]
        print(f"Listed companies count: {len(listed)}")
        
        # Print top 5
        print(listed.head())
        
        # Save to csv for inspection
        listed.to_csv("listed_companies.csv", index=False)
        
except Exception as e:
    print(f"Error inspecting corp_codes: {e}")
