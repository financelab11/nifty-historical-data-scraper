import pandas as pd
import json
import requests
import sys
import os

# Supabase configuration
SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_indices"

def upload_to_supabase(csv_file, index_name_override):
    if not os.path.exists(csv_file):
        print(f"File {csv_file} not found. Skipping.")
        return

    print(f"Reading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # Force index_name
    df['index_name'] = index_name_override
    
    # Ensure columns match DB: date, index_name, open, high, low, close
    needed_cols = ["date", "index_name", "open", "high", "low", "close"]
    for col in needed_cols:
        if col not in df.columns:
            df[col] = 0.0 # Default value
            
    # Keep only needed columns
    df = df[needed_cols]
    
    # Handle '-' values by converting to 0
    df = df.replace('-', 0)
    
    # Ensure numeric types
    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    # Convert to list of dicts
    records = df.to_dict(orient='records')
    
    print(f"Uploading {len(records)} records for {index_name_override} to Supabase...")
    
    # Supabase REST API endpoint for the table with upsert on conflict of (date, index_name)
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
    indices_files = [
        ("nifty_50_data.csv", "Nifty 50"),
        ("nifty_next_50_data.csv", "Nifty Next 50"),
        ("nifty_midcap_150_data.csv", "Nifty Midcap 150"),
        ("nifty_500_data.csv", "Nifty 500"),
        ("nifty_smallcap_250_data.csv", "Nifty Smallcap 250"),
        ("nifty_microcap250_data.csv", "Nifty Microcap 250"),
        ("nifty_smallcap_500_data.csv", "Nifty Smallcap 500"),
        ("nifty_total_mkt_data.csv", "Nifty Total Market"),
        ("nifty500_momentum_50_data.csv", "Nifty500 Momentum 50"),
        ("nifty500_quality_50_data.csv", "Nifty500 Quality 50"),
        ("nifty500_value_50_data.csv", "Nifty500 Value 50"),
        ("nifty500_low_volatility_50_data.csv", "Nifty500 Low Volatility 50"),
        # New Indices
        ("nifty100_low_volatility_30_data.csv", "NIFTY100 LOW VOLATILITY 30"),
        ("nifty100_quality_30_data.csv", "NIFTY100 QUALITY 30"),
        ("nifty100_alpha_30_data.csv", "NIFTY100 ALPHA 30"),
        ("nifty200_quality_30_data.csv", "NIFTY200 QUALITY 30"),
        ("nifty_midcap150_quality_50_data.csv", "NIFTY MIDCAP150 QUALITY 50"),
        ("nifty200_momentum_30_data.csv", "NIFTY200 MOMENTUM 30"),
        ("nifty200_alpha_30_data.csv", "NIFTY200 ALPHA 30"),
        ("nifty_midcap150_momentum_50_data.csv", "NIFTY MIDCAP150 MOMENTUM 50"),
        ("nifty_smallcap250_quality_50_data.csv", "NIFTY SMALLCAP250 QUALITY 50"),
        ("nifty_smallcap250_momentum_quality_100_data.csv", "NIFTY SMALLCAP250 MOMENTUM QUALITY 100"),
        ("nifty_midsmallcap400_momentum_quality_100_data.csv", "NIFTY MIDSMALLCAP400 MOMENTUM QUALITY 100"),
        ("nifty500_multicap_momentum_quality_50_data.csv", "NIFTY500 MULTICAP MOMENTUM QUALITY 50"),
        ("nifty500_multifactor_mqvlv_50_data.csv", "NIFTY500 MULTIFACTOR MQVLv 50"),
        ("nifty_total_market_momentum_quality_50_data.csv", "Nifty Total Market Momentum Quality 50")
    ]
    
    for filename, index_name in indices_files:
        upload_to_supabase(filename, index_name)
