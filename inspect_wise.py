import pandas as pd
from io import StringIO

def inspect_wise():
    with open('wise_report.html', 'r', encoding='utf-8') as f:
        html = f.read()

    try:
        dfs = pd.read_html(StringIO(html))
        print(f"Found {len(dfs)} tables")
        for i, df in enumerate(dfs):
            print(f"--- Table {i} ---")
            print(df.columns.tolist())
            print(df.head(3))
            print("\n")
    except Exception as e:
        print(f"Error parsing html: {e}")

if __name__ == "__main__":
    inspect_wise()
