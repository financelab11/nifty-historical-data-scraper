from nsepython import *
import pandas as pd
import json
import requests
import sys

# Configuration
SYMBOL = "Nifty500 Momentum 50"
START_DATE = "01-Apr-2005"
END_DATE = "27-Feb-2026"
SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIyMTUyNTcsImV4cCI6MjA4Nzc5MTI1N30.VAUQC2in2zbVj_qYLEbpTOEFWdzaUwniOI-bGZqJg9o"
TABLE_NAME = "nifty_momentum_50"

def fetch_data():
    print(f"Fetching data for {SYMBOL} from {START_DATE} to {END_DATE}...")
    try:
        data = index_history(SYMBOL, START_DATE, END_DATE)
        print(f"  Fetched {len(data)} rows.")
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def prepare_data(df):
    print("Preparing data...")
    # Clean column names
    rename_map = {
        "Index Name": "index_name",
        "HistoricalDate": "date",
        "OPEN": "open",
        "HIGH": "high",
        "LOW": "low",
        "CLOSE": "close"
    }
    df.rename(columns=rename_map, inplace=True)
    
    # Select columns
    cols = ["date", "index_name", "open", "high", "low", "close"]
    df = df[[c for c in cols if c in df.columns]]
    
    # Handle '-' values
    for col in ["open", "high", "low", "close"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Parse and format date
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df.dropna(subset=['date'], inplace=True)
    df.sort_values('date', inplace=True)
    df.drop_duplicates(subset=['date'], inplace=True)
    
    # Format date for Supabase (YYYY-MM-DD)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    return df

def upload_to_supabase(df):
    records = df.to_dict(orient='records')
    print(f"Uploading {len(records)} records to Supabase...")
    
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?on_conflict=date"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    chunk_size = 500
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        try:
            resp = requests.post(url, headers=headers, json=chunk)
            resp.raise_for_status()
            print(f"  Uploaded chunk {i//chunk_size + 1} ({len(chunk)} rows)")
        except Exception as e:
            print(f"  Error uploading chunk: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response: {e.response.text}")

def main():
    df = fetch_data()
    if df is not None and not df.empty:
        df = prepare_data(df)
        upload_to_supabase(df)
        print("Done!")
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()
