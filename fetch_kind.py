import pandas as pd
import requests
from io import BytesIO

def get_krx_code():
    url = "http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"
    print(f"Downloading from {url} with headers...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            print("Download successful. Parsing...")
            # Use BytesIO to handle bytes content
            tables = pd.read_html(BytesIO(res.content), header=0, encoding='euc-kr')
            df = tables[0]
            print(f"Downloaded {len(df)} companies.")
            
            # Rename columns standardly
            df = df.rename(columns={'회사명': 'Name', '종목코드': 'Code'})
            df['Code'] = df['Code'].astype(str).str.zfill(6)
            print(df.head())
            return df
        else:
            print(f"Failed with status: {res.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    get_krx_code()
