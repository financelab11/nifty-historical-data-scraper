from nsepython import index_history
from datetime import datetime
import pandas as pd

symbol = "NIFTY 100 LOW VOLATILITY 30"
start_date = "01-Apr-2005"
end_date = "28-Feb-2026"

print(f"Testing {symbol}...")
try:
    df = index_history(symbol, start_date, end_date)
    if df is not None and not df.empty:
        print(f"Success! Found {len(df)} rows.")
        print(df.head())
    else:
        print("No data found.")
except Exception as e:
    print(f"Failed: {e}")
