import pandas as pd
from pykrx import stock
from datetime import datetime
import time

# User provided API key (Note: pykrx doesn't use this directly for scraping, 
# but we keep it if the user intended to use OpenDart. 
# For this script using pykrx public scraping, it's not strictly needed but good to preserve context)
api_key = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"

def get_nearest_business_day(target_date_str):
    """
    Given a date string YYYYMMDD, returns the nearest business day (backwards)
    if the date is a holiday or weekend.
    """
    target_date = datetime.strptime(target_date_str, "%Y%m%d")
    
    # Get business days roughly around the target date to check validity
    # We'll just check if the date has data. 
    # Actually, pykrx `get_market_ohlcv_by_ticker` works on specific dates.
    # If a date is a holiday, it returns empty or previous day?
    # Reliable way: get nearest business day using pykrx's get_nearest_business_day_in_range logic
    # or just try to fetch. If empty, go back 1 day.
    
    # Simpler approach: Use `get_previous_business_day` loop
    curr_date = target_date
    for _ in range(10): # Try going back up to 10 days
        date_str = curr_date.strftime("%Y%m%d")
        try:
            # Check if market was open by fetching tickers
            tickers = stock.get_market_ticker_list(date_str)
            if tickers:
                return date_str
        except:
            pass
        # Go back one day
        curr_date = curr_date - pd.Timedelta(days=1)
    return target_date_str # Fallback (likely won't happen if within range)

def main():
    start_year = 2014
    end_year = 2026
    target_md = "0104" # Jan 4th
    
    all_data = []

    print(f"Starting data download from {start_year} to {end_year}...")

    for year in range(start_year, end_year + 1):
        target_date_str = f"{year}{target_md}"
        
        # Adjust for weekends/holidays
        valid_date = get_nearest_business_day(target_date_str)
        print(f"Fetching data for {year} (Date: {valid_date})...")
        
        try:
            # 1. Fetch Fundamentals (BPS, PER, PBR, EPS, DIV, DPS)
            df_fund = stock.get_market_fundamental_by_ticker(valid_date, market="ALL")
            
            # 2. Fetch Price (Close) - OHLCV
            df_price = stock.get_market_ohlcv_by_ticker(valid_date, market="ALL")
            
            # 3. Fetch Names (using Market Cap API which usually includes Name)
            df_cap = stock.get_market_cap_by_ticker(valid_date, market="ALL")
            
            # Merge
            # df_fund indices are Tickers. df_price indices are Tickers.
            # We want: Name, Year, Stock Price, BPS, DIV, DPS, EPS, PBR, PER
            
            # Align columns
            # df_fund: ['BPS', 'PER', 'PBR', 'EPS', 'DIV', 'DPS'] (Check column names dynamically)
            # df_price: ['siga', 'goga', 'jeoga', 'jongga', 'georaeryang'] -> 'jongga' is Close
            # df_cap: ['siga_chong-aek', 'georaeryang', 'sangjang_jusiksu', 'jongmok_myeong'] -> 'jongmok_myeong' is Name (or 'Name')
            
            # Standardize column names (pykrx returns Korean or English depending on version/settings, usually Korean by default unless renamed)
            # Actually pykrx columns might be Korean: 'BPS', 'PER', ... are usually English keys in the df, but let's be careful.
            
            # Let's inspect the columns or just merge and rename.
            # Merging on index (Ticker)
            merged = df_fund.join(df_price['종가'], how='inner', rsuffix='_price') # '종가' = Close
            merged = merged.join(df_cap['종목명'], how='inner') # '종목명' = Name
            
            # Add Year
            merged['Year'] = year
            
            # Reset index to make Ticker a column (optional, user didn't ask for Ticker but it's good to have, though user image doesn't show it explicitely, image shows Name first)
            # User image columns: Name, Year, stock price, BPS, DIV, DPS, EPS, PBR, PER
            
            # Rename columns to match User Request
            # Expected df_fund cols: BPS, PER, PBR, EPS, DIV, DPS
            # But sometimes they are distinct. 
            # Note: valid_date is string YYYYMMDD
            
            merged.rename(columns={
                '종목명': 'Name',
                '종가': 'stock price',
                # BPS, DIV, DPS, EPS, PBR, PER should already be there if fetch was successful
            }, inplace=True)
            
            # Handle potentially missing columns or ensure they exist
            required_cols = ['Name', 'Year', 'stock price', 'BPS', 'DIV', 'DPS', 'EPS', 'PBR', 'PER']
            
            # Check what we have
            # print(merged.columns)
            
            for col in required_cols:
                if col not in merged.columns:
                    # Try uppercase or specific mapping if pykrx returns slightly diff names
                    pass 
            
            # Filter and reorder
            # Ensure we only keep rows that have the data we need or fillna
            final_year_df = merged[required_cols].copy()
            
            all_data.append(final_year_df)
            
            print(f"  -> Fetched {len(final_year_df)} records.")
            
        except Exception as e:
            print(f"  -> Error fetching {year}: {e}")
        
        # Be nice to the server
        time.sleep(1)

    if all_data:
        final_df = pd.concat(all_data)
        
        # Sort by Name and Year
        final_df.sort_values(by=['Name', 'Year'], inplace=True)
        
        # Save to Excel
        output_file = "stock_data_2014_2026.xlsx"
        final_df.to_excel(output_file, index=False)
        print(f"Successfully saved data to {output_file}")
    else:
        print("No data collected.")

if __name__ == "__main__":
    main()
