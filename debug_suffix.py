import FinanceDataReader as fdr
import sys

def test_ticker(ticker):
    print(f"Testing ticker: {ticker}")
    try:
        df = fdr.DataReader(ticker, '2024-01-01', '2024-01-10')
        if not df.empty:
            print(f"Success (No Suffix)! Shape: {df.shape}")
            return
        else:
            print("Failed (No Suffix).")
    except:
        print("Error (No Suffix)")

    # Try KS (KOSPI)
    try:
        print(f"Testing {ticker}.KS ...")
        df = fdr.DataReader(f"{ticker}.KS", '2024-01-01', '2024-01-10')
        if not df.empty:
            print(f"Success (.KS)! Shape: {df.shape}")
            return
    except:
         print("Error (.KS)")

    # Try KQ (KOSDAQ)
    try:
        print(f"Testing {ticker}.KQ ...")
        df = fdr.DataReader(f"{ticker}.KQ", '2024-01-01', '2024-01-10')
        if not df.empty:
            print(f"Success (.KQ)! Shape: {df.shape}")
            return
    except:
         print("Error (.KQ)")

if __name__ == "__main__":
    # Test 003020 (KISCO Holdings, KOSPI)
    test_ticker("003020")
    # Test 032150 (Often fails in logs)
    test_ticker("032150")
