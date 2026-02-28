import pandas as pd
import json
import requests
import cloudscraper
from datetime import datetime, timedelta
import time
import os

# ── Configuration ─────────────────────────────────────────────────────────────

SYMBOL = "NIFTY 50"
START_DATE_STR = "01-Apr-2005"
# Today is 28-Feb-2026
END_DATE_STR = "28-Feb-2026"

# Supabase configuration
SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_indices"

def fetch_nifty_historical_official(symbol, start_date, end_date):
    print(f"Fetching {symbol} from {start_date} to {end_date} via niftyindices.com API...")
    scraper = cloudscraper.create_scraper()
    url = "https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString"
    
    # The API expects a POST request where the entire payload is a stringified JSON inside 'cinfo'
    inner_payload = {
        "name": symbol,
        "startDate": start_date,
        "endDate": end_date
    }
    
    payload = {"cinfo": json.dumps(inner_payload)}
    
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = scraper.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            raw_data = response.json()['d']
            if raw_data == "No Data Found":
                print(f"No data found for {start_date} to {end_date}")
                return pd.DataFrame()
            
            data = json.loads(raw_data)
            df = pd.DataFrame(data)
            return df
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Exception during fetch: {e}")
        return pd.DataFrame()

def process_data(df, symbol):
    if df.empty:
        return df

    # Standardize column names
    rename_map = {
        "HistoricalDate": "date",
        "OPEN": "open",
        "HIGH": "high",
        "LOW": "low",
        "CLOSE": "close",
        "Index Name": "index_name"
    }
    df.rename(columns=rename_map, inplace=True)
    
    # Ensure index_name is set correctly
    df['index_name'] = "Nifty 50"
    
    # Parse Date (Official format is typically DD-MMM-YYYY or similar)
    # The API returns data where HistoricalDate is like '01 Apr 2005'
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df.dropna(subset=['date'], inplace=True)
    
    # Sort by date
    df.sort_values('date', inplace=True)
    
    # Coerce numeric columns and handle '-' or other non-numeric as null
    for col in ["open", "high", "low", "close"]:
        if col in df.columns:
            # First remove commas from numbers like "1,234.50"
            df[col] = df[col].astype(str).str.replace(',', '')
            df[col] = pd.to_numeric(df[col].replace('-', '0'), errors='coerce')
    
    # Remove duplicates
    df.drop_duplicates(subset=['date', 'index_name'], inplace=True)
    
    # Format Date for DB
    df['date_str'] = df['date'].dt.strftime("%Y-%m-%d")
    
    # Select final columns
    final_df = df[['date_str', 'index_name', 'open', 'high', 'low', 'close']].copy()
    final_df.rename(columns={'date_str': 'date'}, inplace=True)
    
    return final_df

def upload_to_supabase(df):
    if df.empty:
        print("No data to upload.")
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
    
    # Upload in chunks
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
    
    print("Upload complete!")

def main():
    # Since 2005 to 2026 is a long range, and niftyindices API might have limits,
    # let's fetch year by year to be safe and robust.
    
    start_year = 2005
    end_year = 2026
    
    all_dfs = []
    
    for year in range(start_year, end_year + 1):
        y_start = f"01-Jan-{year}"
        if year == 2005:
            y_start = "01-Apr-2005"
            
        y_end = f"31-Dec-{year}"
        if year == 2026:
            y_end = "28-Feb-2026"
            
        df_year = fetch_nifty_historical_official(SYMBOL, y_start, y_end)
        if not df_year.empty:
            print(f"  Found {len(df_year)} rows for {year}")
            all_dfs.append(df_year)
        else:
            print(f"  No data or error for {year}")
        
        time.sleep(2) # Throttle
        
    if all_dfs:
        full_df = pd.concat(all_dfs)
        processed_df = process_data(full_df, SYMBOL)
        print(f"Total processed rows: {len(processed_df)}")
        upload_to_supabase(processed_df)
    else:
        print("Failed to fetch any data.")

if __name__ == "__main__":
    main()
