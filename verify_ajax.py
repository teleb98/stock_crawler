import requests
import re
import pandas as pd
from io import StringIO

def check_ajax(code):
    # 1. Get Encparam
    url_main = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Referer': f'https://finance.naver.com/item/main.naver?code={code}'
    }
    
    s = requests.Session()
    res = s.get(url_main, headers=headers)
    
    # Extract encparam
    match = re.search(r"encparam: '([^']+)'", res.text)
    if not match:
        print("Encparam not found")
        return

    encparam = match.group(1)
    print(f"Encparam: {encparam}")

    # 2. Call AJAX
    # cF1001.aspx is the "Financial Statement" (Trend)
    url_ajax = "https://navercomp.wisereport.co.kr/v2/company/ajax/cF1001.aspx"
    params = {
        'cmp_cd': code,
        'fin_typ': '0', # 0: Consolidated, 4: Separate
        'freq_typ': 'Y', # Y: Annual
        'encparam': encparam,
        # 'id': '?' # Check if needed
    }
    
    headers_ajax = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': url_main
    }

    res_ajax = s.get(url_ajax, params=params, headers=headers_ajax)
    print(f"AJAX Status: {res_ajax.status_code}")
    
    if res_ajax.status_code == 200:
        try:
            dfs = pd.read_html(StringIO(res_ajax.text))
            for i, df in enumerate(dfs):
                print(f"Table {i} Columns: {df.columns.tolist()}")
                # Check for 2019 or 2020
                print(df.head())
        except Exception as e:
            print(f"Parsing error: {e}")
            print(res_ajax.text[:500])

if __name__ == "__main__":
    check_ajax("005930")
