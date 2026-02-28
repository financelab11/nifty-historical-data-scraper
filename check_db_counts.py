import pandas as pd
import requests
import json

SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_indices"

def check_counts():
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=index_name,date"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        df = pd.DataFrame(data)
        if not df.empty:
            summary = df.groupby('index_name').agg({'date': ['count', 'min', 'max']})
            print(summary)
        else:
            print("No data found.")
    else:
        print(f"Error: {resp.status_code}")
        print(resp.text)

if __name__ == "__main__":
    check_counts()
