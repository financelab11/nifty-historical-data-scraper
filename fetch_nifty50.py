import requests
import json
import pandas as pd
from datetime import datetime
import time
import os

# Supabase configuration
SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_indices"

# API Endpoint
url = "https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString"

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://www.niftyindices.com",
    "Referer": "https://www.niftyindices.com/reports/historical-data",
    "X-Requested-With": "XMLHttpRequest"
}

def fetch_chunk(symbol, start_date, end_date):
    inner_payload = {
        "name": symbol,
        "startDate": start_date,
        "endDate": end_date
    }
    payload = {"cinfo": json.dumps(inner_payload)}
    
    with requests.Session() as session:
        try:
            # Initialize cookies
            session.get("https://www.niftyindices.com", headers=headers, timeout=15)
            
            # POST to the historical data endpoint
            response = session.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                raw_data = response.json().get('d')
                if raw_data:
                    data_list = json.loads(raw_data)
                    return pd.DataFrame(data_list)
            else:
                print(f"Request failed for {symbol}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    return None

def upload_to_supabase(df, index_name):
    print(f"Uploading {len(df)} records for {index_name} to Supabase...")
    
    # Ensure correct columns and handle missing values
    needed_cols = ["date", "index_name", "open", "high", "low", "close"]
    for col in needed_cols:
        if col not in df.columns:
            df[col] = 0.0
            
    # Standardize types and clean
    df = df[needed_cols]
    df = df.replace('-', 0)
    
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
    symbol = "NIFTY 50"
    start_year = 2005
    end_year = datetime.now().year
    
    all_dfs = []
    
    # Process year by year for robustness
    for current_year in range(start_year, end_year + 1):
        start_date = f"01-Jan-{current_year}"
        if current_year == 2005:
            start_date = "01-Apr-2005"
        
        end_date = f"31-Dec-{current_year}"
        if current_year == end_year:
            # Current date
            end_date = datetime.now().strftime("%d-%b-%Y")
            
        print(f"Fetching {symbol} from {start_date} to {end_date}...")
        df = fetch_chunk(symbol, start_date, end_date)
        
        if df is not None and not df.empty:
            print(f"  Found {len(df)} rows.")
            all_dfs.append(df)
        else:
            print(f"  No data found for {current_year}.")
            
        time.sleep(1.5) # Polite delay
        
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        
        # Rename columns to match DB
        rename_map = {
            "Index Name": "index_name",
            "IndexName": "index_name",
            "HistoricalDate": "date",
            "OPEN": "open",
            "HIGH": "high",
            "LOW": "low",
            "CLOSE": "close"
        }
        final_df.rename(columns=rename_map, inplace=True)
        final_df['index_name'] = symbol
        
        # Ensure all columns are numeric
        for col in ["open", "high", "low", "close"]:
            if col in final_df.columns:
                final_df[col] = pd.to_numeric(final_df[col].replace(',', '', regex=True), errors='coerce').fillna(0)
        
        # Parse date and sort
        final_df['date'] = pd.to_datetime(final_df['date'], dayfirst=True, errors='coerce')
        final_df.dropna(subset=['date'], inplace=True)
        final_df.sort_values('date', inplace=True)
        final_df.drop_duplicates(subset=['date'], inplace=True)
        
        # Format date for Supabase
        final_df['date'] = final_df['date'].dt.strftime('%Y-%m-%d')
        
        # Final cleanup and upload
        upload_to_supabase(final_df, symbol)
        print(f"NIFTY 50 update complete. Total rows: {len(final_df)}")
    else:
        print("No NIFTY 50 data fetched.")

if __name__ == "__main__":
    main()
