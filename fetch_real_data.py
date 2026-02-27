import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import os

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

def main():
    # Use standard names recognized by the website
    symbols = ["Nifty500 Momentum 50", "Nifty500 Quality 50"]
    start_year = 2005
    end_year = 2026
    
    for symbol in symbols:
        all_data = []
        current_year = start_year
        while current_year <= end_year:
            start_date = f"01-Jan-{current_year}"
            if current_year == 2005:
                start_date = "01-Apr-2005"
            
            end_date = f"31-Dec-{current_year}"
            if current_year == 2026:
                end_date = "27-Feb-2026"
                
            print(f"Fetching {symbol} from {start_date} to {end_date}...")
            df = fetch_chunk(symbol, start_date, end_date)
            
            if df is not None and not df.empty:
                print(f"  Found {len(df)} rows.")
                all_data.append(df)
            else:
                print(f"  No data found for {current_year}.")
                
            current_year += 1
            time.sleep(2) # Be extra polite
            
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            # Rename columns to standard format
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
            
            # Ensure index_name is correct
            final_df['index_name'] = symbol
            
            # Clean up columns - keep only what we need
            needed_cols = ["date", "index_name", "open", "high", "low", "close"]
            final_df = final_df[[c for c in needed_cols if c in final_df.columns]]
            
            # Parse date and sort
            final_df['date'] = pd.to_datetime(final_df['date'], dayfirst=True, errors='coerce')
            final_df.dropna(subset=['date'], inplace=True)
            final_df.sort_values('date', inplace=True)
            final_df.drop_duplicates(subset=['date'], inplace=True)
            
            # Format date for Supabase
            final_df['date'] = final_df['date'].dt.strftime('%Y-%m-%d')
            
            filename = f"{symbol.lower().replace(' ', '_')}_data.csv"
            final_df.to_csv(filename, index=False)
            print(f"Saved {len(final_df)} rows to {filename}")
        else:
            print(f"No data fetched for {symbol}.")

if __name__ == "__main__":
    main()
