import pandas as pd
import json
import requests
import sys
import os

# Supabase configuration
# Use environment variables if possible, but keep hardcoded as fallback for now for reliability in this specific task
SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_momentum_50"

def upload_to_supabase(csv_file):
    print(f"Reading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # Standardize columns for DB
    df.columns = [c.lower() for c in df.columns]
    
    # Add index_name if missing
    if 'index_name' not in df.columns:
        df['index_name'] = "Nifty500 Momentum 50"
    
    # Handle '-' values by converting to 0 or None
    # My scraper already handles this, but let's be safe.
    df = df.replace('-', 0)
    
    # Convert to list of dicts
    records = df.to_dict(orient='records')
    
    print(f"Uploading {len(records)} records to Supabase...")
    
    # Supabase REST API endpoint for the table
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?on_conflict=date"
    
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
            sys.exit(1)
  
    print("Upload complete!")

if __name__ == "__main__":
    upload_to_supabase("Nifty500_Momentum50_20050630_20250630.csv")
