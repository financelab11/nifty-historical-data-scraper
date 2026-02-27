from nsepython import index_history
import pandas as pd
from datetime import datetime
import time

# ── Configuration ─────────────────────────────────────────────────────────────

INDEX_NAME = "Nifty500 Momentum 50"
START_DATE = "30-Jun-2005"
END_DATE   = datetime.now().strftime("%d-%b-%Y")
OUTPUT_CSV = "Nifty500_Momentum50_20050630_20250630.csv"

def main():
    print(f"Fetching historical data for {INDEX_NAME} from {START_DATE} to {END_DATE}...")
    
    try:
        # nsepython handles larger date ranges by splitting internally.
        df = index_history(INDEX_NAME, START_DATE, END_DATE)
        
        if df is None or df.empty:
            print("Error: No data fetched.")
            return

        print(f"Raw columns: {df.columns.tolist()}")
        
        # Standardise column names
        # Based on test output, common columns are 'HistoricalDate', 'OPEN', 'HIGH', 'LOW', 'CLOSE'
        # Note: IndexName/INDEX_NAME are also present but not useful in a single index CSV.
        rename_map = {
            "HistoricalDate": "Date",
            "OPEN": "Open",
            "HIGH": "High",
            "LOW": "Low",
            "CLOSE": "Close"
        }
        df.rename(columns=rename_map, inplace=True)
        
        # Parse Date
        # The date in raw response is often 'DD-MMM-YYYY' or 'DD MMM YYYY'
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        
        # Sort by date
        df.sort_values('Date', inplace=True)
        
        # Coerce numeric columns and handle '-' as null
        for col in ["Open", "High", "Low", "Close"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].replace('-', '0'), errors='coerce')
        
        # Remove duplicates
        df.drop_duplicates(subset=['Date'], inplace=True)
        
        # Format Date for CSV
        df['Date'] = df['Date'].dt.strftime("%Y-%m-%d")
        
        # Reorder columns to a clean format
        # Filter only existing columns
        existing_cols = [c for c in ['Date', 'Open', 'High', 'Low', 'Close'] if c in df.columns]
        df = df[existing_cols]
        
        # Save to CSV
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"Successfully saved {len(df)} rows to {OUTPUT_CSV}")
        print("\nPreview (last 5 rows):")
        print(df.tail())
        
    except Exception as e:
        print(f"Scraper failed: {e}")

if __name__ == "__main__":
    main()
