import pandas as pd
import OpenDartReader
import os
import sys
import time
from tqdm import tqdm
import concurrent.futures

# --- AUTO-CORRECT ENVIRONMENT ---
venv_python = "/Users/mac/.gemini/antigravity/scratch/kr_stock_data/venv/bin/python"
if os.path.exists(venv_python) and os.path.abspath(sys.executable) != os.path.abspath(venv_python):
    print(f">> Switching to VENV: {venv_python}")
    try:
        os.execv(venv_python, [venv_python] + sys.argv)
    except OSError:
        pass
# --------------------------------

API_KEY = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"
INPUT_FILE = "/Users/mac/.gemini/antigravity/brain/360ae226-87b3-4ba5-9763-a57fb0870727/stock_data_2014_2026.xlsx"
OUTPUT_FILE = "/Users/mac/.gemini/antigravity/brain/360ae226-87b3-4ba5-9763-a57fb0870727/stock_data_enriched.xlsx"

def get_corp_code_map(dart):
    print("Fetching Corp Code Map...")
    try:
        df = dart.corp_codes
        # map stock_code -> corp_code
        # stock_code might be missing or padded?
        # df['stock_code'] is usually string "005930"
        return dict(zip(df['stock_code'].str.strip(), df['corp_code']))
    except Exception as e:
        print(f"Error fetching corp codes: {e}")
        return {}

def fetch_fin_year(dart, corp_code, year):
    """
    Fetch Net Income and Equity for BPS/EPS Calc
    """
    try:
        # 11011 = Business Report (Annual)
        # For 2024 data, it might not be fully available if report not filed?
        # Usually 2023 report is available. 2024 might be quarterly?
        # Let's try 11011. If fails, return 0s.
        
        # reprt_code: 11011 (Annual), 11013 (1Q), 11012 (Half), 11014 (3Q)
        # financial statements
        df = dart.finstate(corp=corp_code, bsns_year=str(year), reprt_code='11011')
        
        if df is None or df.empty:
            return None
            
        # We need Consolidated (connected) typically, usually returns multiple limits.
        # fs_div: CFS (Consolidated), OFS (Separate) -> Prefer CFS
        
        equity = 0
        net_income = 0
        
        # Filter for Consolidated if available, else Separate
        df_target = df[df['fs_div'] == 'CFS']
        if df_target.empty:
            df_target = df[df['fs_div'] == 'OFS']
            
        if df_target.empty:
            return None
            
        # Find Equity (자본총계)
        # account_nm like '자본총계'
        # normalizing text
        
        def parse_amount(x):
            try:
                return float(str(x).replace(',',''))
            except:
                return 0.0

        for _, row in df_target.iterrows():
            acct = row['account_nm']
            amt = parse_amount(row['thstrm_amount'])
            
            if '자본총계' in acct:
                equity = amt
            elif '당기순이익' in acct and '손실' not in acct: # Simplistic check
                net_income = amt
            elif '당기순이익' in acct: # Covering both
                net_income = amt
                
        return {'equity': equity, 'net_income': net_income}
        
    except Exception:
        return None

def fetch_div_year(dart, corp_code, year):
    try:
        # Dividend api
        # dart.report(..., dsp_th=...) no unique api?
        # list() -> '배당' keyword?
        # There is no direct "dividend" table API in simple open dart reader?
        # Actually dart.finstate doesn't give DPS.
        # But wait, User just wants fundamentals.
        # There is a report named '배당에 관한 사항' but parsing text is hard.
        # For calculation, we might skip DIV/DPS if too hard, or just do EPS/BPS.
        # Let's verify standard Opendart support for dividends.
        # It's usually in 'fnlttSinglAcntAll' maybe?
        
        # Let's stick to BPS/EPS first (Net Income/Equity).
        return {'dps': 0}
    except:
        return {'dps': 0}

def main():
    print("Loading existing data...")
    if not os.path.exists(INPUT_FILE):
        print("Input file not found.")
        return

    df_base = pd.read_excel(INPUT_FILE, dtype={'Year': int})
    
    # Filter targets: 2023, 2024 only
    # Note: 2024 Annual Report might NOT be out yet (Jan 2026 implies 2024 is done, but currently we are running in simulated 2026? Yes. 2024 report comes out Mar 2025.)
    # In 'current time' of user context... 2026.
    # So 2023 and 2024 should be available.
    
    targets = df_base[df_base['Year'].isin([2023, 2024])]
    unique_names = targets['Name'].unique()
    
    # We need Ticker (Stock Code) from somewhere.
    # The current Excel only has Name?
    # Wait, previous script dropped Code?
    # 'stock_downloader_final.py' had 'Code' in all_rows but dropped it before saving?
    # "if 'Code' in final_df.columns: pass"
    # Yes, it dropped it.
    # WE NEED THE CODE to use OpenDart.
    # I have to re-map Name -> Ticker? Or re-run the downloader to keep Code?
    # Re-mapping Name -> Ticker is safer using OpenDart's list.
    
    dart = OpenDartReader(API_KEY)
    ticker_map = get_corp_code_map(dart) 
    # This maps StockCode -> CorpCode.
    # But we have Names in Excel.
    # We need Name -> StockCode -> CorpCode.
    
    # Let's build Name -> CorpCode map
    df_corp = dart.corp_codes
    name_to_corp = dict(zip(df_corp['corp_name'].str.strip(), df_corp['corp_code']))
    
    # Also Map Name -> StockCode for logging/verification
    name_to_stock = dict(zip(df_corp['corp_name'].str.strip(), df_corp['stock_code']))
    
    print(f"Enriching {len(unique_names)} companies for 2023-2024...")
    
    results = {} # (Name, Year) -> {BPS, EPS, PER, PBR}
    
    # Limit number of requests?
    # 2500 companies * 2 years = 5000 requests.
    # Multithreading recommended?
    # OpenDart limit 10k/day.
    
    # CAUTION: Name collisions? (Samsung Electronics vs Samsung Eng)
    # Ticker matching is better. 
    # Since I don't have Ticker in Excel, Name is the only key.
    
    for name in tqdm(unique_names):
        corp_code = name_to_corp.get(name)
        if not corp_code:
            continue
            
        # Process years
        for year in [2023, 2024]:
            t_data = fetch_fin_year(dart, corp_code, year)
            if t_data:
                 results[(name, year)] = t_data
                 
    # Update DataFrame
    print("Updating values...")
    # This is slow row-by-row.
    # Vectorized update?
    
    # We need Market Cap ( 시가총액 ) to calc PER/PBR?
    # No, PER = Price / EPS. PBR = Price / BPS.
    # We have 'stock price' in Excel.
    # Shares? We need Shares to calc EPS/BPS from Income/Equity.
    # Marcap had 'Stocks' (Shares) but we dropped it too?
    # Ah.
    
    # CRITICAL: We dropped 'Stocks' (Shares) in the final downloader.
    # Without Shares, calculating EPS/BPS from Equity/Income is hard.
    # Unless OpenDart returns per-share data directly?
    # OpenDart 'finstate' returns raw index amounts (Equity, Income).
    
    # SOLUTION: I must re-run the Downloader to KEEP 'Code' and 'Stocks' (Shares) columns.
    # Then I can run this enricher.
    
    print("CRITICAL: Missing 'Shares' info to calculate ratios.")
    print("Please re-run the downloader retaining the 'Stocks' column first.")

if __name__ == "__main__":
    main()
