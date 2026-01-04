from marcap import marcap_data
import pandas as pd

def verify_marcap():
    print("Testing Marcap...")
    try:
        # Fetch data for a specific date range
        df = marcap_data('2024-01-01', '2024-01-10')
        print(f"Data Shape: {df.shape}")
        print("Columns:", df.columns.tolist())
        print(df.head())
        
        # Check for Samsung (005930)
        samsung = df[df['Code'] == '005930']
        print("\nSamsung Sample:")
        print(samsung[['Code', 'Name', 'Close', 'PER', 'PBR', 'EPS', 'BPS']])
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_marcap()
