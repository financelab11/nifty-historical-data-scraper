from nsepython import index_history
import pandas as pd
from datetime import datetime
import time
import os

# ── Configuration ─────────────────────────────────────────────────────────────

SYMBOLS = [
    "Nifty 100 Low Volatility 30",
    "Nifty 100 Quality 30",
    "Nifty 100 Alpha 30",
    "Nifty 200 Quality 30",
    "Nifty Midcap 150 Quality 50",
    "Nifty 200 Momentum 30",
    "Nifty 200 Alpha 30",
    "Nifty Midcap 150 Momentum 50",
    "Nifty Smallcap 250 Quality 50",
    "Nifty Smallcap 250 Momentum Quality 100",
    "Nifty MidSmallcap 400 Momentum Quality 100",
    "Nifty 500 Multicap Momentum Quality 50",
    "Nifty 500 Multifactor MQVLv 50",
    "Nifty Total Market Momentum Quality 50"
]
START_DATE = "01-Apr-2005"
END_DATE   = "28-Feb-2026"

def fetch_index_data(symbol):
    print(f"Fetching historical data for {symbol} from {START_DATE} to {END_DATE}...")
    
    try:
        # nsepython handles larger date ranges by splitting internally.
        df = index_history(symbol, START_DATE, END_DATE)
        
        if df is None or df.empty:
            print(f"Error: No data fetched for {symbol}.")
            return None

        # Standardise column names
        rename_map = {
            "HistoricalDate": "date",
            "OPEN": "open",
            "HIGH": "high",
            "LOW": "low",
            "CLOSE": "close",
            "IndexName": "index_name",
            "Index Name": "index_name"
        }
        df.rename(columns=rename_map, inplace=True)
        
        # Ensure index_name is correct (standardize)
        df['index_name'] = symbol
        
        # Parse Date
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        df.dropna(subset=['date'], inplace=True)
        
        # Sort by date
        df.sort_values('date', inplace=True)
        
        # Coerce numeric columns and handle '-' as null
        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].replace('-', '0'), errors='coerce')
        
        # Remove duplicates
        df.drop_duplicates(subset=['date'], inplace=True)
        
        # Format Date for CSV
        df['date'] = df['date'].dt.strftime("%Y-%m-%d")
        
        # Reorder columns
        needed_cols = ["date", "index_name", "open", "high", "low", "close"]
        existing_cols = [c for c in list(df.columns) if c in needed_cols]
        df = df[existing_cols]
        
        # Ensure all columns exist
        for col in needed_cols:
            if col not in df.columns:
                df[col] = 0.0
        
        df = df[needed_cols]
        
        filename = f"{symbol.lower().replace(' ', '_')}_data.csv"
        df.to_csv(filename, index=False)
        print(f"Successfully saved {len(df)} rows to {filename}")
        return df
        
    except Exception as e:
        print(f"Scraper failed for {symbol}: {e}")
        return None

def main():
    for symbol in SYMBOLS:
        fetch_index_data(symbol)
        time.sleep(1)

if __name__ == "__main__":
    main()
