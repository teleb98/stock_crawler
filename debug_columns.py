from pykrx import stock

date = "20240104"
df = stock.get_market_fundamental_by_ticker(date, market="ALL")
print("Columns:", df.columns.tolist())
print("Head:", df.head())
