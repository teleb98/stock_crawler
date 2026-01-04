import OpenDartReader
import pandas as pd

API_KEY = "1222951ca96bedb0bdbb8645b0ca0ad948d6c557"

def check_dart_info(codes):
    dart = OpenDartReader(API_KEY)
    df = dart.corp_codes
    
    print("Checking Codes in OpenDart DB:")
    for code in codes:
        row = df[df['stock_code'] == code]
        if not row.empty:
            print(f"\nCode: {code}")
            print(row.iloc[0])
        else:
            print(f"\nCode: {code} NOT FOUND in OpenDart")

if __name__ == "__main__":
    check_dart_info(["003020", "032150", "040130"])
