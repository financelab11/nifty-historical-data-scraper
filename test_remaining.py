from nsepython import index_history
import pandas as pd
from datetime import datetime
import time

SYMBOLS = [
    "NIFTY 100 LOW VOLATILITY 30",
    "NIFTY 100 QUALITY 30",
    "NIFTY 200 MOMENTUM 30"
]
START_DATE = "01-Apr-2005"
END_DATE   = "28-Feb-2026"

def fetch(symbol):
    print(f"Fetching {symbol}...")
    df = index_history(symbol, START_DATE, END_DATE)
    if df is not None and not df.empty:
        filename = f"{symbol.lower().replace(' ', '_')}_data.csv"
        df.to_csv(filename, index=False)
        print(f"Success! {len(df)} rows.")
    else:
        print(f"Failed {symbol}")

for s in SYMBOLS:
    fetch(s)
    time.sleep(1)
