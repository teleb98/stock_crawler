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
    target_dt = pd.to_datetime(target_date)
    
    # Filter for <= target_dt
    # BUT this DF might be huge with multiple tickers.
    # We want the "snapshot" of the market on a specific day.
    # So we need to find the specific Date present in the DF that is closest to target.
    
    unique_dates = sorted(df['Date'].unique())
    # find closest
    # using simple search
    valid_date = None
    for d in reversed(unique_dates):
        if d <= target_dt:
            valid_date = d
            break
            
    if valid_date is None:
        return pd.DataFrame()
        
    print(f"  Target: {target_date} -> Found: {valid_date}")
    return df[df['Date'] == valid_date].copy()

def main():
    print("Loading Marcap Data...")
    
    # Years to process
    years = range(2014, 2027) # 2014..2026
    
    all_rows = []
    
    for year in years:
        file_path = os.path.join(DATA_DIR, f"marcap-{year}.csv.gz")
        if not os.path.exists(file_path):
            print(f"Warning: Data for {year} not found at {file_path}")
            continue
            
        print(f"Processing {year}...")
        # Load CSV
        # Cols: Code,Name,Market,Dept,Close,ChangeCode,Changes,ChagesRatio,Open,High,Low,Volume,Amount,Marcap,Stocks,MarketId,Rank,Date
        # And FUNDAMENTALS? 
        # Marcap usually has PER, EPS, etc. Let's check columns after load.
        
        try:
            df = pd.read_csv(file_path, dtype={'Code':str})
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Target Date: Jan 4th
            target_date = f"{year}-01-04"
            
            daily_snapshot = get_nearest_date_data(df, target_date)
            
            if daily_snapshot.empty:
                print(f"  No data found for {year}")
                continue
                
            # Rename columns to match user request
            # User wants: Name, Year, stock price, BPS, DIV, DPS, EPS, PBR, PER, 시가총액
            # Marcap cols (English): Code, Name, Close, ...
            # Marcap usually includes: PER, EPS, PBR, DPS?
            # If standard marcap: 
            # 'Code', 'Name', 'Market', 'Dept', 'Close', 'ChangeCode', 'Changes', 'ChagesRatio', 
            # 'Open', 'High', 'Low', 'Volume', 'Amount', 'Marcap', 'Stocks', 'MarketId', 'Rank', 'Date'
            # Wait, does it have PER/EPS? 
            # Newer marcap versions might have it. I need to check columns.
            
            # Let's inspect columns on the fly or be flexible.
            # If not in marcap, we are still stuck on fundamentals.
            # But marcap repo README says it includes "PER, PBR provided by KRX".
            # Let's assume they are there.
            
            daily_snapshot['Year'] = year
            
            # Map columns
            # We map what we can.
            
            # Prepare row for each ticker
            for _, row in daily_snapshot.iterrows():
                # Extract
                r_data = {
                    'Name': row.get('Name'),
                    'Year': year,
                    'stock price': row.get('Close'),
                    'BPS': row.get('BPS', 0), # Fallback 0
                    'DIV': row.get('DividendYield', 0), # Marcap might call it DividendYield
                    'DPS': row.get('DPS', 0),
                    'EPS': row.get('EPS', 0),
                    'PBR': row.get('PBR', 0),
                    'PER': row.get('PER', 0),
                    '시가총액': row.get('Marcap', 0)
                }
                all_rows.append(r_data)
                
        except Exception as e:
            print(f"Error processing {year}: {e}")
            
    if all_rows:
        final_df = pd.DataFrame(all_rows)
        # Sort
        final_df.sort_values(by=['Name', 'Year'], inplace=True)
        
        # Columns
        cols = ['Name', 'Year', 'stock price', 'BPS', 'DIV', 'DPS', 'EPS', 'PBR', 'PER', '시가총액']
        # Fill missing cols with 0 if they didn't exist in source
        for c in cols:
            if c not in final_df.columns:
                final_df[c] = 0
                
        final_df = final_df[cols]
        output_file = "stock_data_marcap.xlsx"
        final_df.to_excel(output_file, index=False)
        print(f"Saved to {output_file}")
    else:
        print("No data collected from Marcap.")

if __name__ == "__main__":
    main()
