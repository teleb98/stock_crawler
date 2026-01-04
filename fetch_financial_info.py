import sys

try:
    import OpenDartReader
except ImportError:
    print("\n\033[91mError: OpenDartReader library not found.\033[0m")
    print("It looks like you are running this script with the system Python.")
    print("Please use the provided helper script to run with the correct environment:")
    print("\n    \033[92m./run_fetch.sh\033[0m\n")
    sys.exit(1)
import pandas as pd
import time

def main():
    # 1. Initialize OpenDartReader
    # API KEY provided by the user
    api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
    dart = OpenDartReader(api_key)

    print("OpenDartReader initialized.")

    # 2. Define Target Companies
    # Sample list of major Korean companies
    companies = ['삼성전자', 'SK하이닉스', '현대자동차', 'NAVER', '카카오']
    
    # Year to fetch (using 2023 as 2024 annual reports might not be fully out yet or just to be safe for a sample)
    target_year = '2023' 
    
    # Report code: '11011' (Business Report/Annual), '11012' (Half), '11013' (1Q), '11014' (3Q)
    # Using Annual Report
    reprt_code = '11011' 

    all_data = []

    print(f"Fetching financial data for {target_year}...")

    # 3. Fetch Data
    for corp_name in companies:
        try:
            print(f"Fetching {corp_name}...")
            # finstate returns the financial statement
            # fs_div: 'CFS' (Consolidated), 'OFS' (Separate)
            # using Consolidated by default
            df = dart.finstate(corp_name, target_year, reprt_code=reprt_code)
            
            if df is None or df.empty:
                print(f"  - No data found for {corp_name}")
                continue

            # Add company name column for clarity if not present or just to be sure
            # OpenDart usually provides 'corp_name' but let's ensure it's there
            if 'corp_name' not in df.columns:
                df['corp_name'] = corp_name
            
            # Select relevant columns to keep the output clean
            # We mostly care about Account Name, Amount, etc.
            # This varies by user need, but for a sample, we keep standard columns.
            # Common columns: 'rcept_no', 'bsns_year', 'corp_code', 'stock_code', 'account_nm', 'fs_div', 'fs_nm', 'sj_div', 'sj_nm', 'thstrm_nm', 'thstrm_amount', ...
            
            all_data.append(df)
            
            # Be nice to the API
            time.sleep(0.5) 
            
        except Exception as e:
            print(f"  - Error fetching {corp_name}: {e}")

    # 4. Save to Excel
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        
        output_file = "financial_data.xlsx"
        final_df.to_excel(output_file, index=False)
        print(f"\nSuccess! Data saved to {output_file}")
        print(f"Total rows fetched: {len(final_df)}")
    else:
        print("\nNo data was collected.")

if __name__ == "__main__":
    main()
