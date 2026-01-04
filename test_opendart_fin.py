import OpenDartReader

API_KEY = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"

def test_opendart_fin():
    dart = OpenDartReader(API_KEY)
    
    # Samsung Electronics (005930) -> Corp Code needed? 
    # OpenDartReader usually handles ticker but better to find corp_code
    # Let's try direct ticker
    
    print("Fetching Financials for Samsung (005930) - 2023...")
    try:
        # 11011 = Business Report (Annual)
        df = dart.finstate(corp='005930', bsns_year='2023', reprt_code='11011')
        if df is not None and not df.empty:
            print("Success!")
            print(df[['fs_nm', 'account_nm', 'thstrm_amount']].head(10))
            
            # Check for EPS/BPS?
            # It usually returns Balance Sheet/Income Statement.
            # We need to Calculate or find "Main Account"
            # Does it have 'Earnings Per Share'?
            print("\nSearching for EPS/BPS...")
            print(df[df['account_nm'].str.contains('Share|주당|자본|이익', na=False)])
            
        else:
            print("No data returned.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_opendart_fin()
