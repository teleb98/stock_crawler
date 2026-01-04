import pandas as pd
import os

output_file = "stock_data_2014_2026.xlsx"

if not os.path.exists(output_file):
    print("File not found!")
else:
    print(f"File found: {output_file}")
    df = pd.read_excel(output_file)
    print(f"Shape: {df.shape}")
    print("Columns:", df.columns.tolist())
    print("\nSample Data:")
    print(df.head())
    
    # Check for specific companies if possible
    # "3S" is usually code 060310? Or just search by Name
    try:
        sample = df[df['Name'].str.contains("3S") | df['Name'].str.contains("AJ네트웍스")]
        print("\nSpecific Sample (3S, AJ Networks):")
        print(sample)
    except:
        pass
