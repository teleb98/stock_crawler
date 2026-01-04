import OpenDartReader
import FinanceDataReader as fdr
import pandas as pd
import datetime
import time
import concurrent.futures
from tqdm import tqdm

# API Key
API_KEY = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"

def fetch_data_for_ticker(stock_code, corp_name, start_year, end_year):
    results = []
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"
    
    try:
        df_price = fdr.DataReader(stock_code, start_date, end_date)
        if df_price.empty:
            return []
            
        df_price.index = pd.to_datetime(df_price.index)
        
        for year in range(start_year, end_year + 1):
            target_dt = pd.Timestamp(f"{year}-01-04")
            past_data = df_price[df_price.index <= target_dt]
            if past_data.empty:
                continue
            recent_row = past_data.iloc[-1]
            row = {
                'Name': corp_name,
                'Year': year,
                'stock price': recent_row['Close'],
                'BPS': 0, 'DIV': 0, 'DPS': 0, 'EPS': 0, 'PBR': 0, 'PER': 0, '시가총액': 0
            }
            results.append(row)
    except:
        pass
    return results

def main():
    print("Fetching Corporation List (Test Run)...")
    dart = OpenDartReader(API_KEY)
    try:
        df_corp = dart.corp_codes
    except:
        print("Using internal method to fetch codes...")
        df_corp = pd.DataFrame() # Fallback
        
    df_listed = df_corp[df_corp['stock_code'].str.strip() != '']
    df_listed = df_listed.drop_duplicates(subset=['stock_code'])
    print(f"Total Tickers: {len(df_listed)}")
    
    # LIMIT FOR TEST
    # Limit for testing
    # FORCE SAMSUNG (005930) to be in the list
    samsung = df_listed[df_listed['stock_code'] == '005930']
    other_samples = df_listed.head(5)
    
    df_test = pd.concat([samsung, other_samples])
    stocks_to_process = df_test.to_dict('records')
    print(f"Processing {len(stocks_to_process)} tickers for test (including Samsung)...")
    
    start_year = 2014
    end_year = 2026
    all_data = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_data_for_ticker, item['stock_code'], item['corp_name'], start_year, end_year): item for item in stocks_to_process}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(stocks_to_process)):
            res = future.result()
            if res:
                all_data.extend(res)
            
    if all_data:
        final_df = pd.DataFrame(all_data)
        final_df.sort_values(by=['Name', 'Year'], inplace=True)
        cols = ['Name', 'Year', 'stock price', 'BPS', 'DIV', 'DPS', 'EPS', 'PBR', 'PER', '시가총액']
        final_df = final_df[cols]
        output_file = "stock_data_test.xlsx"
        final_df.to_excel(output_file, index=False)
        print(f"Saved to {output_file}")
    else:
        print("No data collected.")

if __name__ == "__main__":
    main()
