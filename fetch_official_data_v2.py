from nsepython import index_history
import pandas as pd
from datetime import datetime
import time
import requests
import os

# ── Configuration ─────────────────────────────────────────────────────────────

# Explicitly fetching both as benchmarks/strategies
SYMBOLS = ["Nifty 50", "Nifty Smallcap 250"]
START_DATE = "01-Apr-2005"
END_DATE   = "28-Feb-2026" # Today

# Supabase configuration for direct upload
SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_indices"

def fetch_and_upload(symbol):
    print(f"\n--- Processing {symbol} ---")
    print(f"Fetching historical data from {START_DATE} to {END_DATE}...")
    
    try:
        # nsepython internally splits large date ranges (it works for 20+ years!)
        df = index_history(symbol, START_DATE, END_DATE)
        
        if df is None or df.empty:
            print(f"Error: No data fetched for {symbol}.")
            return False

        # Rename columns to match database schema
        # nsepython returns: Index Name, Index Date, Open, High, Low, Close, Volume, Turnover, P/E, P/B, Div Yield
        # Sometimes keys differ slightly
        rename_map = {
            "HistoricalDate": "date",
            "Index Date": "date",
            "OPEN": "open",
            "Open": "open",
            "HIGH": "high",
            "High": "high",
            "LOW": "low",
            "Low": "low",
            "CLOSE": "close",
            "Close": "close",
            "IndexName": "index_name",
            "Index Name": "index_name"
        }
        df.rename(columns=rename_map, inplace=True)
        
        # Ensure correct index_name
        df['index_name'] = symbol
        
        # Parse and sort by date
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        df.dropna(subset=['date'], inplace=True)
        df.sort_values('date', inplace=True)
        
        # Remove duplicates
        df.drop_duplicates(subset=['date', 'index_name'], inplace=True)
        
        # Data Cleaning: Handle '-' and ensure numeric
        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).replace('-', '0'), errors='coerce').fillna(0)
        
        # Format for Supabase/CSV
        df['date'] = df['date'].dt.strftime("%Y-%m-%d")
        
        # Filter columns
        final_cols = ["date", "index_name", "open", "high", "low", "close"]
        df = df[final_cols]
        
        total_rows = len(df)
        print(f"Scraped {total_rows} rows.")
        
        # Upload to Supabase
        records = df.to_dict(orient='records')
        url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?on_conflict=date,index_name"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        
        chunk_size = 500
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]
            resp = requests.post(url, headers=headers, json=chunk)
            resp.raise_for_status()
            print(f"  Uploaded chunk {i//chunk_size + 1} ({len(chunk)} rows)")
            
        print(f"Successfully updated {symbol} in DB.")
        return True
        
    except Exception as e:
        print(f"Failed for {symbol}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def main():
    for symbol in SYMBOLS:
        fetch_and_upload(symbol)
        time.sleep(5) # Delay to prevent throttling

if __name__ == "__main__":
    main()
