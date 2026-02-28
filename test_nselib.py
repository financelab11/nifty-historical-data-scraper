from nselib import capital_market
import pandas as pd

SYMBOLS = ["NIFTY 100 QUALITY 30", "NIFTY 100 LOW VOLATILITY 30", "NIFTY 200 MOMENTUM 30"]

for s in SYMBOLS:
    print(f"Trying {s} with nselib...")
    try:
        # nselib uses DD-MM-YYYY
        df = capital_market.index_history(s, "01-01-2024", "28-02-2026")
        if df is not None and not df.empty:
            print(f"Success! {len(df)} rows.")
            filename = f"{s.lower().replace(' ', '_')}_data.csv"
            df.to_csv(filename, index=False)
        else:
            # Try without space after NIFTY
            s2 = s.replace("NIFTY ", "NIFTY")
            print(f"Trying {s2}...")
            df = capital_market.index_history(s2, "01-01-2024", "28-02-2026")
            if df is not None and not df.empty:
                print(f"Success! {len(df)} rows.")
                filename = f"{s2.lower().replace(' ', '_')}_data.csv"
                df.to_csv(filename, index=False)
            else:
                print(f"Failed {s}")
    except Exception as e:
        print(f"Error for {s}: {e}")
