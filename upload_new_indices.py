import pandas as pd
import requests
import os

# Supabase configuration
SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
# Service Role Key for upsert permissions
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_indices"

def upload_to_supabase(csv_file):
    if not os.path.exists(csv_file):
        print(f"File {csv_file} not found. Skipping.")
        return

    print(f"Reading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # Standardize columns for DB
    df.columns = [c.lower() for c in df.columns]
    
    # Ensure columns match DB: date, index_name, open, high, low, close
    needed_cols = ["date", "index_name", "open", "high", "low", "close"]
    for col in needed_cols:
        if col not in df.columns:
            df[col] = 0.0 # Default value
            
    # Keep only needed columns
    df = df[needed_cols]
    
    # Convert to list of dicts
    records = df.to_dict(orient='records')
    
    index_name = df['index_name'].iloc[0]
    print(f"Uploading {len(records)} records for {index_name} to Supabase...")
    
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?on_conflict=date,index_name"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    # Upload in chunks of 500
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
    
    print(f"Upload complete for {csv_file}!")

if __name__ == "__main__":
    files = [
        "nifty_next_50_data.csv",
        "nifty_midcap_150_data.csv",
        "nifty_500_data.csv",
        "nifty_smallcap_250_data.csv",
        "nifty_microcap250_data.csv",
        "nifty_smallcap_500_data.csv",
        "nifty_total_mkt_data.csv"
    ]
    
    for filename in files:
        upload_to_supabase(filename)
