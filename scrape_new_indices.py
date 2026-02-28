from nsepython import index_history
import pandas as pd
from datetime import datetime
import time
import os

# ── Configuration ─────────────────────────────────────────────────────────────

# Mapping of Friendly Name -> NSE/NiftyIndices API Symbol
SYMBOLS_MAP = {
    "NIFTY100 LOW VOLATILITY 30": "NIFTY100 LOWVOL30",
    "NIFTY100 QUALITY 30": "NIFTY100 QUALTY30",
    "NIFTY100 ALPHA 30": "NIFTY100 ALPHA 30",
    "NIFTY200 QUALITY 30": "NIFTY200 QUALITY 30",
    "NIFTY MIDCAP150 QUALITY 50": "NIFTY MIDCAP150 QUALITY 50",
    "NIFTY200 MOMENTUM 30": "NIFTY200MOMENTM30",
    "NIFTY200 ALPHA 30": "NIFTY200 ALPHA 30",
    "NIFTY MIDCAP150 MOMENTUM 50": "NIFTY MIDCAP150 MOMENTUM 50",
    "NIFTY SMALLCAP250 QUALITY 50": "Nifty Smallcap250 Quality 50",
    "NIFTY SMALLCAP250 MOMENTUM QUALITY 100": "NIFTY SMALLCAP250 MOMENTUM QUALITY 100",
    "NIFTY MIDSMALLCAP400 MOMENTUM QUALITY 100": "Nifty Midsmallcap400 Momentum Quality 100",
    "NIFTY500 MULTICAP MOMENTUM QUALITY 50": "NIFTY500 MULTICAP MOMENTUM QUALITY 50",
    "NIFTY500 MULTIFACTOR MQVLv 50": "NIFTY500 MQVLv50",
    "Nifty Total Market Momentum Quality 50": "Nifty Total Market Momentum Quality 50"
}

START_DATE = "01-Apr-2005"
END_DATE   = "28-Feb-2026"

def fetch_index_data(friendly_name, api_symbol):
    print(f"Fetching historical data for {friendly_name} (Symbol: {api_symbol}) from {START_DATE} to {END_DATE}...")
    
    try:
        df = index_history(api_symbol, START_DATE, END_DATE)
        
        if df is None or df.empty:
            print(f"Error: No data fetched for {friendly_name}.")
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
        
        # Ensure index_name is correct (standardize to Friendly Name for DB consistency)
        df['index_name'] = friendly_name
        
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
        
        filename = f"{friendly_name.lower().replace(' ', '_')}_data.csv"
        df.to_csv(filename, index=False)
        print(f"Successfully saved {len(df)} rows to {filename}")
        return df
        
    except Exception as e:
        print(f"Scraper failed for {friendly_name}: {e}")
        return None

def main():
    for friendly_name, api_symbol in SYMBOLS_MAP.items():
        fetch_index_data(friendly_name, api_symbol)
        time.sleep(1)

if __name__ == "__main__":
    main()
