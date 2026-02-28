import requests
import os

SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_indices"

url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=index_name,date.min(),date.max(),count"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

try:
    # First, just get index names and counts
    url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=index_name"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    
    counts = {}
    for row in data:
        name = row['index_name']
        counts[name] = counts.get(name, 0) + 1
        
    print("Existing Indices in Database:")
    for name, count in sorted(counts.items()):
        print(f"  {name}: {count} records")
        
except Exception as e:
    print(f"Error checking indices: {e}")
