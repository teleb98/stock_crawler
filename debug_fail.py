import FinanceDataReader as fdr
import sys

def test_ticker(ticker):
    print(f"Testing ticker: {ticker}")
    try:
        df = fdr.DataReader(ticker, '2024-01-01', '2024-01-10')
        if not df.empty:
            print(f"Success! Shape: {df.shape}")
            print(df.head(1))
        else:
            print("Empty dataframe returned.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test one that failed in logs
    test_ticker("003020")
    # Test Samsung again
    test_ticker("005930")
