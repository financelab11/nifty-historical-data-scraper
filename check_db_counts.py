import pandas as pd
import requests
import json

SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_indices"

def check_counts():
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=index_name"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    all_data = []
    offset = 0
    limit = 2000 # Supabase can handle larger chunks if configured, but let's stick to 1000 or use range
    
    while True:
        # Use Range header
        headers["Range"] = f"{offset}-{offset+limit-1}"
        resp = requests.get(url, headers=headers)
        if resp.status_code in [200, 206]:
            data = resp.json()
            if not data:
                break
            all_data.extend(data)
            offset += limit
            if len(data) < limit:
                break
        else:
            print(f"Error: {resp.status_code}")
            print(resp.text)
            break
            
    if all_data:
        df = pd.DataFrame(all_data)
        summary = df.groupby('index_name').size()
        print(summary)
    else:
        print("No data found.")

if __name__ == "__main__":
    check_counts()
