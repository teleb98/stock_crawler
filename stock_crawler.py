import requests
import re
import pandas as pd
from io import StringIO
import time
from datetime import datetime

import os

def get_encparam(code, session):
    url = f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    try:
        res = session.get(url, headers=headers, timeout=10)
        match = re.search(r"encparam: '([^']+)'", res.text)
        if match:
            return match.group(1)
    except Exception as e:
        # print(f"[{code}] Error fetching encparam: {e}")
        pass
    return None

def get_financial_data(code, name, session):
    # 1. Get Encparam
    encparam = get_encparam(code, session)
    if not encparam:
        # print(f"[{name}] Failed to get encparam")
        return None
    
    # 2. AJAX Request
    url_ajax = "https://navercomp.wisereport.co.kr/v2/company/ajax/cF1001.aspx"
    params = {
        'cmp_cd': code,
        'fin_typ': '0', # Consolidated
        'freq_typ': 'Y', # Annual
        'encparam': encparam
    }
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': f"https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd={code}"
    }
    
    try:
        res = session.get(url_ajax, params=params, headers=headers, timeout=10)
        if res.status_code != 200:
            return None
        
        # 3. Parse HTML
        dfs = pd.read_html(StringIO(res.text))
        if len(dfs) < 2:
            return None
            
        # Table 1 typically contains the main financial summary
        df = dfs[1]
        
        # Simplify Columns
        new_columns = []
        for col in df.columns:
            if isinstance(col, tuple):
                val = col[1]
                date_match = re.search(r'\d{4}/\d{2}', val)
                if date_match:
                    new_columns.append(date_match.group(0))
                else:
                    new_columns.append(col[0])
            else:
                new_columns.append(col)
        
        df.columns = new_columns
        df.set_index(df.columns[0], inplace=True)
        return df

    except Exception as e:
        return None

def process_data(df, code, name):
    target_map = {
        'EPS(원)': 'EPS',
        'PER(배)': 'PER',
        'BPS(원)': 'BPS',
        'PBR(배)': 'PBR',
        '현금DPS(원)': 'DPS',
        '현금배당수익률': '배당수익률',
        '발행주식수(보통주)': '발행주식수'
    }
    
    extracted = {}
    
    for row_name, key in target_map.items():
        if row_name in df.index:
            extracted[key] = df.loc[row_name]
        else:
            found = False
            for idx in df.index:
                if key in str(idx) or row_name.split('(')[0] in str(idx):
                    extracted[key] = df.loc[idx]
                    found = True
                    break
            if not found:
                pass

    if not extracted:
        return None

    result_df = pd.DataFrame(extracted)
    result_df = result_df.apply(pd.to_numeric, errors='coerce')
    
    # Calculate derived fields: Stock Price, Market Cap
    # User requested BPS based calculation (Price = BPS * PBR)
    # This is often more stable than PER which can be NaN for loss-making companies
    result_df['주가'] = result_df['BPS'] * result_df['PBR']
    result_df['참고_시가총액(억원)'] = (result_df['주가'] * result_df['발행주식수']) / 100000000 # Convert to Eok Won for readability
    
    result_df.reset_index(inplace=True)
    result_df.rename(columns={'index': '연도'}, inplace=True)
    result_df['종목명'] = name
    result_df['종목코드'] = code
    
    cols = ['연도', '종목명', '종목코드', '주가', '참고_시가총액(억원)', 'EPS', 'PER', 'BPS', 'PBR', 'DPS', '배당수익률']
    for c in cols:
        if c not in result_df.columns:
            result_df[c] = pd.NA
            
    return result_df[cols]

def get_tickers_from_naver():
    tickers = []
    
    # KOSPI (sosok=0) & KOSDAQ (sosok=1)
    # Each page has 50 items. Approx 40 pages for KOSPI (2000 appx? No, 800+), 35 for KOSDAQ (1700 appx).
    # Safely crawl enough pages.
    markets = [(0, 40), (1, 40)] 
    
    print("Crawling tickers from Naver Ranking (Bypassing KRX block)...")
    
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    
    for sosok, max_page in markets:
        market_name = "KOSPI" if sosok == 0 else "KOSDAQ"
        print(f"Scanning {market_name}...")
        
        for page in range(1, max_page + 1):
            url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}"
            try:
                res = session.get(url, headers=headers)
                # Use a simpler regex or parsing to get codes
                # Links look like: <a href="/item/main.naver?code=005930" class="tltle">삼성전자</a>
                soup = pd.read_html(StringIO(res.text))
                # The main table is usually the second one
                # But read_html might fail if no table found.
                # Let's use regex for speed and robustness against table structure changes
                
                # Regex for code and name
                pattern = r'<a href="/item/main.naver\?code=(\d{6})" class="tltle">([^<]+)</a>'
                matches = re.findall(pattern, res.text)
                
                if not matches:
                    print(f"Page {page} empty or structure changed.")
                    break
                    
                for code, name in matches:
                    tickers.append({'Code': code, 'Name': name})
                
                # print(f"  Page {page} done. ({len(matches)} items)")
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  Page {page} error: {e}")
                
    # Remove duplicates just in case
    df = pd.DataFrame(tickers).drop_duplicates(subset=['Code'])
    print(f"Total Companies Found: {len(df)}")
    return df

def main():
    print("Fetching Ticker List...")
    try:
        # krx_df = fdr.StockListing('KRX') # Blocked
        krx_df = get_tickers_from_naver()
    except Exception as e:
        print(f"Error fetching ticker list: {e}")
        return

    all_data = []
    total = len(krx_df)
    
    # Checkpoint File
    today_str = datetime.now().strftime('%Y%m%d')
    checkpoint_file = f"partial_financials_{today_str}.csv"
    
    print(f"Starting crawl for {total} companies...")
    print(f"Data will be incrementally saved to '{checkpoint_file}'")

    if os.path.exists(checkpoint_file):
        print("Existing checkpoint found. Loading...")
        saved_df = pd.read_csv(checkpoint_file, dtype={'종목코드': str})
        all_data = [saved_df]
        collected_codes = set(saved_df['종목코드'].unique())
        print(f"Resuming from {len(collected_codes)} completed companies.")
    else:
        collected_codes = set()
        # Initialize CSV with header if new
        pd.DataFrame(columns=['연도', '종목명', '종목코드', '주가', '참고_시가총액(억원)', 'EPS', 'PER', 'BPS', 'PBR', 'DPS', '배당수익률']).to_csv(checkpoint_file, index=False, encoding='utf-8-sig')

    session = requests.Session()
    session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=50))
    
    count = 0
    start_time = time.time()
    
    # Iterate
    # Convert to list of dicts for easier looping
    target_list = krx_df[['Code', 'Name']].to_dict('records')
    
    batch_data = []
    
    for item in target_list:
        code = str(item['Code'])
        name = item['Name']
        
        if code in collected_codes:
            count += 1
            continue

        try:
            # print(f"[{count+1}/{total}] Fetching {name}...", end='\r')
            df_raw = get_financial_data(code, name, session)
            
            if df_raw is not None:
                df_processed = process_data(df_raw, code, name)
                if df_processed is not None and not df_processed.empty:
                    batch_data.append(df_processed)
            
            # Reduce delay slightly
            time.sleep(0.05) 

        except KeyboardInterrupt:
            print("\nStopping by user request...")
            break
        except Exception as e:
            # print(f"\nError on {name}: {e}")
            pass
        
        count += 1
        
        if count % 10 == 0:
            elapsed = time.time() - start_time
            print(f"[{count}/{total}] Processed. (Time: {elapsed:.1f}s)", end='\r')

        # Batch Save every 50
        if len(batch_data) >= 50:
            batch_df = pd.concat(batch_data, ignore_index=True)
            batch_df.to_csv(checkpoint_file, mode='a', header=False, index=False, encoding='utf-8-sig')
            all_data.append(batch_df)
            batch_data = []

    # Final flush
    if batch_data:
        batch_df = pd.concat(batch_data, ignore_index=True)
        batch_df.to_csv(checkpoint_file, mode='a', header=False, index=False, encoding='utf-8-sig')
        all_data.append(batch_df)

    print("\nCrawl Complete/Stopped.")
    
    # Re-read full CSV to make sure we have everything clean
    print("Generating final Excel file...")
    final_df = pd.read_csv(checkpoint_file, dtype={'종목코드': str})
    
    excel_name = f"All_Companies_Financials_{today_str}.xlsx"
    final_df.to_excel(excel_name, index=False)
    print(f"Successfully saved to {excel_name}")

if __name__ == "__main__":
    main()

