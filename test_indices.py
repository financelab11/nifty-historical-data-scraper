from nsepython import index_history
from datetime import datetime
import pandas as pd

indices = [
    "Nifty Next 50", 
    "Nifty Midcap 150", 
    "Nifty 500", 
    "Nifty Smallcap 250", 
    "Nifty Microcap 250", 
    "Nifty Smallcap 500", 
    "Nifty Total Market"
]

start_date = "01-Apr-2005"
end_date = "27-Feb-2026"

for index in indices:
    print(f"Testing {index}...")
    try:
        # Just fetch 1 day to test symbol validity
        df = index_history(index, start_date, "05-Apr-2005")
        if df is not None and not df.empty:
            print(f"  OK: Found {len(df)} rows")
        else:
            print(f"  FAILED: No data for {index}")
    except Exception as e:
        print(f"  ERROR for {index}: {e}")
