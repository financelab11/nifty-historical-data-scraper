from nsepython import index_history
import pandas as pd

indices = ["NIFTY MICROCAP 250", "NIFTY TOTAL MARKET", "NIFTY SMALLCAP 500"]
start = "01-Jan-2024"
end = "05-Jan-2024"

for index in indices:
    print(f"Testing {index}...")
    try:
        df = index_history(index, start, end)
        if df is not None and not df.empty:
            print(f"  OK: Found {len(df)} rows")
        else:
            print(f"  FAILED for {index}")
    except Exception as e:
        print(f"  ERROR for {index}: {e}")
