import OpenDartReader
import pandas as pd
import time
import sys
import os
import argparse

# Initial Setup
api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
try:
    dart = OpenDartReader(api_key)
except Exception as e:
    print(f"Error initializing OpenDartReader: {e}")
    sys.exit(1)

# Configuration
# Reports to fetch: Year and Report Code (11011 = Annual)
TARGET_YEARS = ['2024', '2021', '2018']
REPORT_CODE = '11011' 

OUTPUT_CSV = 'all_financials_raw.csv'
OUTPUT_EXCEL = 'all_financials_2018_2024.xlsx'

# Argument Parsing
parser = argparse.ArgumentParser(description='OpenDart Financial Downloader')
parser.add_argument('--limit', type=int, help='Limit number of companies for testing', default=None)
parser.add_argument('--code', type=str, help='Target specific company code for testing', default=None)
args = parser.parse_args()

LIMIT = args.limit 
TARGET_CODE = args.code 

def get_listed_companies():
    print("Fetching company list...")
    try:
        df = dart.corp_codes
        # Clean stock_code: ensure string, strip whitespace
        df['stock_code'] = df['stock_code'].astype(str).str.strip()
        
        # Filter for listed companies (stock_code is not empty and not 'nan' and not 'None')
        listed = df[
            (df['stock_code'] != '') & 
            (df['stock_code'] != 'nan') & 
            (df['stock_code'] != 'None')
        ]
        
        print(f"Found {len(listed)} listed companies.")
        return listed
    except Exception as e:
        print(f"Error fetching company list: {e}")
        # Return empty DF
        return pd.DataFrame()

def main():
    listed_companies = get_listed_companies()
    
    if listed_companies.empty:
        print("No companies found. Exiting.")
        return

    if TARGET_CODE:
        print(f"Test mode: target code {TARGET_CODE}")
        listed_companies = listed_companies[listed_companies['stock_code'] == TARGET_CODE]
    elif LIMIT:
        print(f"Test mode: limiting to first {LIMIT} companies.")
        listed_companies = listed_companies.head(LIMIT)
        
    total_companies = len(listed_companies)
    print(f"Starting download for {total_companies} companies...")
    
    # Check if CSV exists to resume
    header_written = False
    if os.path.exists(OUTPUT_CSV) and not (TARGET_CODE or LIMIT):
         pass 

    success_count = 0
    fail_count = 0
    
    # Increase delay to respect API limits (1.0s)
    # 10,000 calls / day limit. 4000 companies * 3 = 12,000 calls.
    # We WILL hit the limit.
    
    for i, (idx, row) in enumerate(listed_companies.iterrows()):
        corp_code = str(row['corp_code']).strip() 
        corp_name = row['corp_name']
        stock_code = row['stock_code']
        
        print(f"[{i+1}/{total_companies}] Processing {corp_name} ({stock_code})...")
        
        company_dfs = []
        
        for year in TARGET_YEARS:
            try:
                # Fetch data
                df = dart.finstate(corp_code, year, reprt_code=REPORT_CODE)
                
                if df is not None and not df.empty:
                    if 'corp_name' not in df.columns:
                        df['corp_name'] = corp_name
                    if 'target_report_year' not in df.columns:
                        df['target_report_year'] = year
                        
                    company_dfs.append(df)
                    # print(f"    > {year}: Found data.")
                else:
                    # print(f"    > {year}: No data.")
                    pass
                    
                time.sleep(0.6) # Increased delay to avoid soft ban
                
            except Exception as e:
                # Log specific errors
                err_msg = str(e)
                if "020" in err_msg or "Limit" in err_msg:
                    print(f"\nCRITICAL: API Limit Reached or Ban Detected! ({e})")
                    print("Stopping execution to preserve data.")
                    return # Exit main loop
                elif "Connection" in err_msg:
                    print(f"    > {year}: Connection Error. Retrying in 5s...")
                    time.sleep(5)
                    try:
                         df = dart.finstate(corp_code, year, reprt_code=REPORT_CODE)
                         if df is not None and not df.empty:
                             company_dfs.append(df)
                    except:
                        print(f"    > {year}: Retry failed.")
                else:
                    # print(f"    > {year}: Error {e}")
                    pass
        
        if company_dfs:
            # Concatenate all years for this company
            company_data = pd.concat(company_dfs, ignore_index=True)
            
            # Save to CSV immediately (Append mode)
            # encoding 'utf-8-sig' for Korean Excel compatibility
            company_data.to_csv(OUTPUT_CSV, mode='a', header=not header_written, index=False, encoding='utf-8-sig')
            
            if not header_written:
                header_written = True
                
            success_count += 1
        else:
            fail_count += 1
            
        # Optional: Print progress every 10 companies
        if (idx + 1) % 10 == 0:
            print(f"  Progress: {success_count} success, {fail_count} no data.")

    print("\nDownload complete.")
    print(f"Total Success: {success_count}")
    print(f"Total No Data: {fail_count}")
    
    # Convert to Excel if CSV exists and has data
    if success_count > 0 and os.path.exists(OUTPUT_CSV):
        print(f"Converting {OUTPUT_CSV} to {OUTPUT_EXCEL}...")
        try:
            df_final = pd.read_csv(OUTPUT_CSV)
            df_final.to_excel(OUTPUT_EXCEL, index=False)
            print(f"Successfully saved to {OUTPUT_EXCEL}")
        except Exception as e:
            print(f"Error converting to Excel: {e}")

if __name__ == "__main__":
    main()
