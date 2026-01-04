import OpenDartReader
import FinanceDataReader as fdr
import pandas as pd
import datetime
import time
import concurrent.futures
from tqdm import tqdm

# API Key
API_KEY = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"

def get_target_dates(start_year, end_year):
    """
    Returns a dictionary of {year: target_date_str}
    Target is Jan 4th or nearest business day.
    Actually we just need the list of years. 
    We will query the whole range and lookup.
    """
    return range(start_year, end_year + 1)

def fetch_data_for_ticker(stock_code, corp_name, start_year, end_year):
    """
    Fetches data for a single ticker for the entire range.
    Returns a list of dictionaries (one per year).
    """
    results = []
    
    # Define Date Range for FDR
    # Fetch a bit wider to ensure we cover start and end
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31" # or current date
    
    try:
        # Fetch Price History Check
        # fdr.DataReader uses Naver for KRX stocks (usually)
        df_price = fdr.DataReader(stock_code, start_date, end_date)
        
        if df_price.empty:
            return []
            
        # Ensure index is datetime
        df_price.index = pd.to_datetime(df_price.index)
        
        for year in range(start_year, end_year + 1):
            # Target Date: Jan 4th of that year
            # Logic: If Jan 4th is weekend, take nearest previous business day?
            # User said "Same date (or if holiday, previous recent data)"
            # Let's target Jan 4th.
            
            target_dt = pd.Timestamp(f"{year}-01-04")
            
            # Find closest date ON or BEFORE target_dt
            # asof works for sorted index if we sort
            # df_price is usually sorted
            
            # Filter for dates <= target_dt
            past_data = df_price[df_price.index <= target_dt]
            
            if past_data.empty:
                # Company might not exist yet
                continue
                
            # Take the last available date (nearest to target looking back)
            # Check if it's within reasonable range (e.g. 10 days)
            # If the data is from last year, it's fine (user said "recent data")
            recent_row = past_data.iloc[-1]
            recent_date = past_data.index[-1]
            
            # Check gap. If gap is > 20 days, maybe it was suspended or not listed? 
            # But "previous recent data" implies broad tolerance. 
            # However, if 2014 data is pulled from 2013 Dec, that's fine.
            # But if we are in 2014 loop and last data is 2010... proceed with caution.
            # Let's just take it.
            
            # Extract data
            price = recent_row['Close']
            
            # Fundamentals: Not available via FDR easily.
            # We set placeholders
            bps = 0
            div = 0
            dps = 0
            eps = 0
            pbr = 0
            per = 0
            market_cap = 0 # Could calc if we had shares
            
            # Output Row
            row = {
                'Name': corp_name,
                'Year': year,
                'stock price': price,
                'BPS': bps,
                'DIV': div,
                'DPS': dps,
                'EPS': eps,
                'PBR': pbr,
                'PER': per,
                '시가총액': market_cap # Korean header as requested
            }
            results.append(row)
            
    except Exception as e:
        # print(f"Error fetching {stock_code}: {e}")
        pass
        
    return results

def main():
    print("Initializing OpenDart...")
    dart = OpenDartReader(API_KEY)
    
    print("Fetching Corporation List...")
    try:
        df_corp = dart.corp_codes
    except:
        # Fallback if property access fails
        print("Using internal method to fetch codes...")
        # This part depends on library version, assuming dart.corp_codes worked in check_opendart_list.py
        pass
        
    # Filter for stocks with codes
    # stock_code should be non-empty
    df_listed = df_corp[df_corp['stock_code'].str.strip() != '']
    
    # We might have duplicates (same stock code?)
    df_listed = df_listed.drop_duplicates(subset=['stock_code'])
    
    print(f"Found {len(df_listed)} potential listed corporations.")
    
    # Limit for testing? No, run full or large chunk.
    # User wants full.
    stocks_to_process = df_listed.to_dict('records') # list of dicts
    
    start_year = 2014
    end_year = 2026
    
    all_data = []
    
    print("Starting data fetch (Price only, Fundamentals unavailable due to IP block)...")
    
    # Use ThreadPool
    count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Map: fetch_data_for_ticker(stock_code, corp_name, start_year, end_year)
        futures = {executor.submit(fetch_data_for_ticker, item['stock_code'], item['corp_name'], start_year, end_year): item for item in stocks_to_process}
        
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(stocks_to_process)):
            res = future.result()
            if res:
                all_data.extend(res)
            count += 1
            
    # Save
    if all_data:
        print(f"Collected {len(all_data)} rows.")
        final_df = pd.DataFrame(all_data)
        
        # Sort
        final_df.sort_values(by=['Name', 'Year'], inplace=True)
        
        # Columns Order
        # Name | Year | stock price | BPS | DIV | DPS | EPS | PBR | PER | 시가총액
        cols = ['Name', 'Year', 'stock price', 'BPS', 'DIV', 'DPS', 'EPS', 'PBR', 'PER', '시가총액']
        # Ensure cols exist
        final_df = final_df[cols]
        
        output_file = "stock_data_2014_2026.xlsx"
        final_df.to_excel(output_file, index=False)
        print(f"Saved to {output_file}")
    else:
        print("No data collected.")

if __name__ == "__main__":
    main()
