import yfinance as yf
import pandas as pd
from datetime import datetime
import requests
import json
import os

# Supabase configuration
SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_indices"

def upload_to_supabase(df, index_name):
    print(f"Uploading {len(df)} records for {index_name} to Supabase...")
    
    # Ensure correct columns and handle missing values
    needed_cols = ["date", "index_name", "open", "high", "low", "close"]
    for col in needed_cols:
        if col not in df.columns:
            df[col] = 0.0
            
    # Standardize types and clean
    df = df[needed_cols].copy()
    
    records = df.to_dict(orient='records')
    
    # Supabase REST API endpoint with upsert
    endpoint = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?on_conflict=date,index_name"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    # Upload in chunks
    chunk_size = 500
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        try:
            resp = requests.post(endpoint, headers=headers, json=chunk)
            resp.raise_for_status()
            print(f"  Uploaded chunk {i//chunk_size + 1} ({len(chunk)} rows)")
        except Exception as e:
            print(f"  Error uploading chunk: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response: {e.response.text}")

def main():
    symbol = "^NSEI" # Yahoo Finance symbol for Nifty 50
    display_name = "Nifty 50"
    start_date = "2005-04-01"
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Fetching {display_name} data from {start_date} to {end_date}...")
    
    try:
        # Fetch data
        df = yf.download(symbol, start=start_date, end=end_date)
        
        if df.empty:
            print("No data fetched from Yahoo Finance.")
            return

        # Reset index to get Date column
        df = df.reset_index()
        
        # Standardize column names
        # yf columns might be multi-index or just 'Open', 'High', etc.
        # We need: date, open, high, low, close
        df.columns = [str(c[0]) if isinstance(c, tuple) else str(c) for c in df.columns]
        df.columns = [c.lower() for c in df.columns]
        
        rename_map = {
            "date": "date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close"
        }
        df = df.rename(columns=rename_map)
        
        # Add index_name
        df['index_name'] = display_name
        
        # Format date for Supabase (YYYY-MM-DD)
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # Sort and clean
        df = df.sort_values('date')
        df = df.drop_duplicates(subset=['date'])
        
        # Handle non-numeric and zeros
        for col in ["open", "high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        # Upload
        upload_to_supabase(df, display_name)
        print(f"Successfully processed {len(df)} records for {display_name}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
