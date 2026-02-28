import requests
import json

SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIyMTUyNTcsImV4cCI6MjA4Nzc5MTI1N30.VAUQC2in2zbVj_qYLEbpTOEFWdzaUwniOI-bGZqJg9o"

indices = [
    "Nifty 50",
    "Nifty Next 50",
    "Nifty Midcap 150",
    "Nifty 500",
    "Nifty Smallcap 250",
    "Nifty Microcap 250",
    "Nifty Smallcap 500",
    "Nifty Total Market"
]

for index in indices:
    url = f"{SUPABASE_URL}/rest/v1/nifty_indices?index_name=eq.{index.replace(' ', '%20')}&select=count"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    try:
        resp = requests.get(url, headers=headers)
        count = resp.json()[0]['count']
        print(f"{index}: {count} rows")
    except Exception as e:
        print(f"Error for {index}: {e}")
