import pandas as pd

file_path = "/Users/mac/.gemini/antigravity/scratch/stock_data_downloader/marcap_repo/data/marcap-2024.parquet"

try:
    df = pd.read_parquet(file_path)
    print("Columns:", df.columns.tolist())
    print("\nSample Data:")
    print(df.head())
    
    # Check for fundamentals
    cols = ['PER', 'EPS', 'PBR', 'BPS', 'DIV', 'DPS']
    found = [c for c in cols if c in df.columns]
    print(f"\nFound Fundamentals: {found}")
    
except Exception as e:
    print(f"Error: {e}")
