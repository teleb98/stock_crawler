import pandas as pd
import os
import glob
from tqdm import tqdm

DATA_DIR = "/Users/mac/.gemini/antigravity/scratch/stock_data_downloader/marcap_repo/data"

def get_nearest_date_data(df, target_date):
    """
    Given a dataframe (year-chunk), find rows for the target date.
    If date missing, go back 1-2 days.
    """
    # Assuming df has 'Date' column as datetime
    # Parquet load usually keeps datetime type? Check.
    # In inspect: Rank int64, Date object (string?) or datetime? 
    # Sample output: 2024-01-02 (looks like timestamp/string).
    
    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'])
        
    target_dt = pd.to_datetime(target_date)
    
    unique_dates = sorted(df['Date'].unique())
    valid_date = None
    for d in reversed(unique_dates):
        if d <= target_dt:
            valid_date = d
            break
            
    if valid_date is None:
        return pd.DataFrame()
        
    # print(f"  Target: {target_date} -> Found: {valid_date}")
    return df[df['Date'] == valid_date].copy()

def main():
    print("Loading Local Marcap Archives (Parquet)...")
    
    # Years to process
    years = range(2014, 2027) # 2014..2026
    
    all_rows = []
    
    for year in tqdm(years, desc="Processing Years"):
        file_path = os.path.join(DATA_DIR, f"marcap-{year}.parquet")
        if not os.path.exists(file_path):
            # print(f"Warning: Data for {year} not found")
            continue
            
        try:
            df = pd.read_parquet(file_path)
            
            # Target Date: Jan 4th
            target_date = f"{year}-01-04"
            
            daily_snapshot = get_nearest_date_data(df, target_date)
            
            if daily_snapshot.empty:
                continue
                
            daily_snapshot['Year'] = year
            
            # Use 'Code' as string ticker
            daily_snapshot['Code'] = daily_snapshot['Code'].astype(str).str.zfill(6)
            
            # Prepare row for each ticker
            # Columns: Code, Name, Close, Marcap, Stocks
            for _, row in daily_snapshot.iterrows():
                r_data = {
                    'Name': row.get('Name'),
                    'Code': row.get('Code'),
                    'Year': year,
                    'stock price': row.get('Close'),
                    'Stocks': row.get('Stocks', 0), # Shares Outstanding
                    'BPS': 0, 
                    'DIV': 0, 
                    'DPS': 0, 
                    'EPS': 0, 
                    'PBR': 0,
                    'PER': 0,
                    '시가총액': row.get('Marcap', 0)
                }
                all_rows.append(r_data)
                
        except Exception as e:
            print(f"Error processing {year}: {e}")
            
    if all_rows:
        print(f"Compiling {len(all_rows)} rows...")
        final_df = pd.DataFrame(all_rows)
        # Sort
        final_df.sort_values(by=['Name', 'Year'], inplace=True)
        
        # Columns
        # We need Code and Stocks for the Enrichment step (Code -> OpenDart, Stocks -> EPS Calc)
        # Name | Code | Year | stock price | Stocks | BPS | DIV | DPS | EPS | PBR | PER | 시가총액
        cols = ['Name', 'Code', 'Year', 'stock price', 'Stocks', 'BPS', 'DIV', 'DPS', 'EPS', 'PBR', 'PER', '시가총액']
        
        # Ensure cols exist
        for c in cols:
            if c not in final_df.columns:
                final_df[c] = 0
                
        final_df = final_df[cols]
        
        output_file = "stock_data_2014_2026.xlsx"
        final_df.to_excel(output_file, index=False)
        print(f"Successfully saved to {output_file}")
    else:
        print("No data collected from Marcap.")

if __name__ == "__main__":
    main()
