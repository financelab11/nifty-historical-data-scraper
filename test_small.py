from nsepython import index_history
import pandas as pd
from datetime import datetime

symbol = "NIFTY200 MOMENTUM 30"
start_date = "01-Jan-2024"
end_date = "28-Feb-2026"

print(f"Testing {symbol} with small date range...")
try:
    df = index_history(symbol, start_date, end_date)
    if df is not None and not df.empty:
        print(f"Success! Found {len(df)} rows.")
    else:
        print("No data found.")
except Exception as e:
    print(f"Failed: {e}")
