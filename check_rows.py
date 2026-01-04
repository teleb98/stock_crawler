import requests
import re
import pandas as pd
from io import StringIO

def check_rows(code):
    url_main = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={code}"
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': f'https://finance.naver.com/item/main.naver?code={code}'}
    s = requests.Session()
    res = s.get(url_main, headers=headers)
    match = re.search(r"encparam: '([^']+)'", res.text)
    if not match: return
    encparam = match.group(1)

    url_ajax = "https://navercomp.wisereport.co.kr/v2/company/ajax/cF1001.aspx"
    params = {'cmp_cd': code, 'fin_typ': '0', 'freq_typ': 'Y', 'encparam': encparam}
    res_ajax = s.get(url_ajax, params=params, headers=headers)
    
    dfs = pd.read_html(StringIO(res_ajax.text))
    df = dfs[1] # Table 1 seems to be the main one
    
    # Set index to the first column (or multi-index)
    # The columns are [('주요재무정보', '주요재무정보'), ('연간', ...)]
    # The first column is the label.
    df.set_index(df.columns[0], inplace=True)
    print("Row Indices:")
    for idx in df.index:
        print(idx)

if __name__ == "__main__":
    check_rows("005930")
