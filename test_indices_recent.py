from nsepython import index_history
import pandas as pd

indices = ["Nifty Microcap 250", "Nifty Total Market"]
test_dates = [("01-Jan-2024", "05-Jan-2024"), ("01-Jan-2005", "05-Jan-2005")]

for index in indices:
    print(f"Testing {index}...")
    for start, end in test_dates:
        try:
            df = index_history(index, start, end)
            if df is not None and not df.empty:
                print(f"  OK for {start}: Found {len(df)} rows")
            else:
                print(f"  FAILED for {start}: No data for {index}")
        except Exception as e:
            print(f"  ERROR for {index} at {start}: {e}")
