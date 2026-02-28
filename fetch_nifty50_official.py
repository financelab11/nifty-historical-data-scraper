from nsepython import index_history
import pandas as pd
import requests
import json
import time

# ── Configuration ─────────────────────────────────────────────────────────────

SYMBOL = "NIFTY 50"
# Requested from 1 April 2005
START_DATE = "01-Apr-2005"
# Today is 28-Feb-2026
END_DATE = "28-Feb-2026"

# Supabase configuration
SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_indices"

def fetch_and_process():
    print(f"Fetching {SYMBOL} from {START_DATE} to {END_DATE} via nsepython (official source)...")
    try:
        # nsepython handles larger date ranges by splitting internally.
        df = index_history(SYMBOL, START_DATE, END_DATE)
        
        if df is None or df.empty:
            print(f"Error: No data fetched for {SYMBOL}.")
            return None

        # Standardise column names
        rename_map = {
            "HistoricalDate": "date",
            "OPEN": "open",
            "HIGH": "high",
            "LOW": "low",
            "CLOSE": "close"
        }
        df.rename(columns=rename_map, inplace=True)
        
        # Ensure index_name is correct
        df['index_name'] = "Nifty 50"
        
        # Parse Date - Official format is '27 Feb 2026'
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        df.dropna(subset=['date'], inplace=True)
        
        # Sort by date
        df.sort_values('date', inplace=True)
        
        # Coerce numeric columns and handle '-' as null
        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '')
                df[col] = pd.to_numeric(df[col].replace('-', '0'), errors='coerce')
        
        # Remove duplicates
        df.drop_duplicates(subset=['date', 'index_name'], inplace=True)
        
        # Format Date for DB
        df['date'] = df['date'].dt.strftime("%Y-%m-%d")
        
        # Reorder and select columns
        needed_cols = ["date", "index_name", "open", "high", "low", "close"]
        df = df[needed_cols]
        
        print(f"Successfully processed {len(df)} rows.")
        return df
        
    except Exception as e:
        print(f"Scraper failed for {SYMBOL}: {e}")
        return None

def upload_to_supabase(df):
    if df is None or df.empty:
        print("Nothing to upload.")
        return

    records = df.to_dict(orient='records')
    print(f"Uploading {len(records)} records for {SYMBOL} to Supabase...")
    
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
    
    print("Upload complete for official NIFTY 50 data!")

if __name__ == "__main__":
    data_df = fetch_and_process()
    upload_to_supabase(data_df)
