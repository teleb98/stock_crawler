import FinanceDataReader as fdr
import pandas as pd

try:
    print("Fetching FDR KRX Listing...")
    df = fdr.StockListing('KRX')
    print("Columns:", df.columns.tolist())
    print(df.head(1).T)
    
    # Check for fundamental columns
    funds = ['PER', 'PBR', 'BPS', 'EPS', 'DIV', 'DPS']
    found = [c for c in funds if c in df.columns]
    print(f"\nFound Fundamentals in FDR Listing: {found}")
    
except Exception as e:
    print(f"Error: {e}")
