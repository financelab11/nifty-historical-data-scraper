from nsepython import index_history
import pandas as pd
from datetime import datetime

symbol = "NIFTY 50"
start_date = "01-Apr-2005"
end_date = "28-Feb-2026"

try:
    # nsepython internally splits the date range if needed
    print(f"Fetching {symbol} from {start_date} to {end_date} via nsepython...")
    df = index_history(symbol, start_date, end_date)
    print(f"Fetched {len(df)} rows")
    print(df.head())
    df.to_csv("nifty50_official_test.csv", index=False)
except Exception as e:
    print(f"Error: {e}")
