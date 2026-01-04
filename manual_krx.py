import requests
import time

def fetch_krx_fundamentals(date_str):
    # date_str: YYYYMMDD
    
    # 1. Generate OTP
    gen_otp_url = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"
    query_url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020506",
        "Origin": "http://data.krx.co.kr",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        # "X-Requested-With": "XMLHttpRequest"
    }

    # Params for "Daily Fundamentals (PER/PBR/Div) for ALL tickers"
    # Corresponding to menu [12021] PER/PBR/Dividend Yield -> Search by Date -> All Markets
    # The BLD code is usually "dbms/MDC/STAT/standard/MDCSTAT03501"
    
    otp_params = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT03501",
        "name": "fileDown",
        "fileType": "csv",
        "url": "dbms/MDC/STAT/standard/MDCSTAT03501",
        "searchType": "1",    # 1: By Date, 2: By Ticker
        "mktId": "ALL",       # All Markets
        "trdDd": date_str,    # Date
        # "share": "1",       # Unit: 1 is usually default or explicitly needed?
        "csvxls_isNo": "false",
    }
    
    # Actually, getting JSON data directly avoids OTP logic (OTP is for file download).
    # We want JSON data to parse in Python.
    # KRX uses `getJsonData.cmd` directly for the table view.
    
    json_params = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT03501",
        "searchType": "1",
        "mktId": "ALL",
        "trdDd": date_str,
        "share": "1",
        "money": "1",
        "csvxls_isNo": "false",
    }
    
    try:
        print(f"Requesting data for {date_str}...")
        resp = requests.post(query_url, data=json_params, headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()
            # The data is usually under a key like 'output' or 'block1'
            if 'output' in data:
                print(f"Success! Data count: {len(data['output'])}")
                if len(data['output']) > 0:
                    print("Sample:", data['output'][0])
                return data['output']
            else:
                print("Keys:", data.keys())
                return None
        else:
            print(f"Status Code: {resp.status_code}")
            print("Text:", resp.text[:200])
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    fetch_krx_fundamentals("20240104")
