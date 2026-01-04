import requests
from bs4 import BeautifulSoup
import re

def check_financial_depth(code):
    url = f"https://finance.naver.com/item/main.naver?code={code}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Find the "Financial Analysis" table
    # Usually class 'tb_type1 mb_20' or id 'content' -> 'section cop_analysis'
    section = soup.find('div', class_='section cop_analysis')
    if not section:
        print("Cop analysis section not found")
        return

    # The table is likely inside
    # Naver often puts the table in a script or just plain html
    # Let's look for dates row
    thead = section.find('thead')
    if thead:
        dates = [th.get_text(strip=True) for th in thead.find_all('th')]
        print("Dates found in header:", dates)
        # Filter for YYYY.MM format to count years
        valid_years = [d for d in dates if re.match(r'\d{4}\.\d{2}', d)]
        print(f"Valid annual columns: {len(valid_years)} ({valid_years})")
    
    # Check if there is a script defining "change_fin_data" or similar which might have more data
    
    # Check outstanding shares for Market Cap calc
    # Usually in "sh_type1" or "wrap_company info"
    # Look for "상장주식수"
    total_share_area = soup.find('div', class_='first')
    if total_share_area:
        text = total_share_area.get_text()
        # It's often in a table
        
    # Another generic search for shares
    # "상장주식수"
    shares = "Unknown"
    for th in soup.find_all('th'):
        if "상장주식수" in th.get_text():
            td = th.find_next_sibling('td')
            if td:
                shares = td.get_text(strip=True)
                break
    print(f"Outstanding Shares: {shares}")

if __name__ == "__main__":
    check_financial_depth("005930")
