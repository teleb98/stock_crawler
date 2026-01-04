import pandas as pd
import OpenDartReader
import os
import sys
import time
from tqdm import tqdm

# --- AUTO-CORRECT ENVIRONMENT ---
venv_python = "/Users/mac/.gemini/antigravity/scratch/kr_stock_data/venv/bin/python"
if os.path.exists(venv_python) and os.path.abspath(sys.executable) != os.path.abspath(venv_python):
    pass 
# --------------------------------

API_KEY = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
INPUT_FILE = "stock_data_2014_2026.xlsx"
OUTPUT_FILE = "stock_data_2014_2026_enriched.xlsx"

def get_corp_code_map(dart):
    print("Fetching Corp Code Map...")
    try:
        df = dart.corp_codes
        # map stock_code -> corp_code
        return dict(zip(df['stock_code'].str.strip(), df['corp_code']))
    except Exception as e:
        print(f"Error fetching corp codes: {e}")
        return {}

def fetch_fin_year(dart, corp_code, year):
    try:
        # 11011 = Annual Report
        df = dart.finstate(corp=corp_code, bsns_year=str(year), reprt_code='11011')
        
        if df is None or df.empty:
            return None
            
        equity = 0
        net_income = 0
        
        # 1. Consolidated (CFS)
        df_target = df[df['fs_div'] == 'CFS']
        if df_target.empty:
            # 2. Separate (OFS)
            df_target = df[df['fs_div'] == 'OFS']
            
        if df_target.empty:
            return None
            
        def parse_amount(x):
            try:
                return float(str(x).replace(',',''))
            except:
                return 0.0

        for _, row in df_target.iterrows():
            acct = row['account_nm']
            amt = parse_amount(row['thstrm_amount'])
            
            # Use '자본총계' for Equity
            # Use '당기순이익' for Net Income
            if '자본총계' in acct:
                equity = amt
            elif '당기순이익' in acct:
                net_income = amt
                
        return {'equity': equity, 'net_income': net_income}
        
    except Exception:
        return None

def main():
    print("Loading data for enrichment...")
    if not os.path.exists(INPUT_FILE):
        print(f"{INPUT_FILE} not found.")
        return

    df = pd.read_excel(INPUT_FILE)
    
    # Filter targets: 2023, 2024
    # Note: 2024 financials might only be partial or unavailable depending on dates.
    # OpenDartReader's '11011' for 2024 might fail if report not submitted yet.
    # We will try.
    target_years = [2023, 2024]
    
    # Map Code -> Corp Code
    dart = OpenDartReader(API_KEY)
    ticker_to_corp = get_corp_code_map(dart)
    
    # Identify unique tickers to process
    unique_tickers = df[df['Year'].isin(target_years)]['Code'].astype(str).str.zfill(6).unique()
    
    print(f"Processing {len(unique_tickers)} companies for {target_years}...")
    
    # Cache for results
    # (Code, Year) -> {equity, net_income}
    financial_cache = {}
    
    for code in tqdm(unique_tickers, desc="Fetching OpenDart"):
        corp_code = ticker_to_corp.get(code)
        if not corp_code:
            continue
            
        for year in target_years:
             # Check if we already have it (unlikely unless repeat)
             data = fetch_fin_year(dart, corp_code, year)
             if data:
                 financial_cache[(code, year)] = data
             # Sleep to respect rate limit?
             # 10k limit. 2500 * 2 = 5000.
             # No aggressive sleep needed, maybe small one?
             # time.sleep(0.05) 
    
    print("Calculating Ratios and Updating DataFrame...")
    
    # Update rows
    updated_rows = []
    
    for _, row in tqdm(df.iterrows(), total=len(df)):
        year = row['Year']
        code = str(row['Code']).zfill(6)
        
        # Default copy
        new_row = row.copy()
        
        if year in target_years:
            fin_data = financial_cache.get((code, year))
            if fin_data:
                equity = fin_data['equity']
                income = fin_data['net_income']
                shares = row['Stocks']
                price = row['stock price']
                
                if shares > 0:
                    eps = income / shares
                    bps = equity / shares
                    
                    # Prevent /0 for Price
                    per = price / eps if eps > 0 else 0
                    pbr = price / bps if bps > 0 else 0
                    
                    new_row['EPS'] = round(eps, 2)
                    new_row['BPS'] = round(bps, 2)
                    new_row['PER'] = round(per, 2)
                    new_row['PBR'] = round(pbr, 2)
                    
        updated_rows.append(new_row)
        
    final_df = pd.DataFrame(updated_rows)
    
    # Clean up columns for User Output
    # Remove 'Code' and 'Stocks' to match request
    cols_to_keep = ['Name', 'Year', 'stock price', 'BPS', 'DIV', 'DPS', 'EPS', 'PBR', 'PER', '시가총액']
    final_df = final_df[cols_to_keep]
    
    final_df.to_excel(OUTPUT_FILE, index=False)
    print(f"Enriched data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
