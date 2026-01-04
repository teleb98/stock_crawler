import FinanceDataReader as fdr
import pandas as pd

def fetch_data_for_ticker(stock_code, corp_name, start_year, end_year):
    print(f"Fetching {stock_code} {corp_name}...")
    results = []
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"
    
    try:
        df_price = fdr.DataReader(stock_code, start_date, end_date)
        print(f"  -> Got dataframe shape: {df_price.shape}")
        if df_price.empty:
            return []
            
        df_price.index = pd.to_datetime(df_price.index)
        
        for year in range(start_year, end_year + 1):
            target_dt = pd.Timestamp(f"{year}-01-04")
            past_data = df_price[df_price.index <= target_dt]
            
            if past_data.empty:
                continue
                
            recent_row = past_data.iloc[-1]
            price = recent_row['Close']
            
            row = {
                'Name': corp_name,
                'Year': year,
                'stock price': price,
                'BPS': 0,
            }
            results.append(row)
            
    except Exception as e:
        print(f"Error: {e}")
        
    return results

if __name__ == "__main__":
    res = fetch_data_for_ticker("005930", "Samsung", 2014, 2026)
    print("Result Rows:")
    for r in res:
        print(r)
