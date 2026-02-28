import requests

SUPABASE_URL = "https://bnlqmjjeqrbfmpxkpdce.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJubHFtamplcXJiZm1weGtwZGNlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjIxNTI1NywiZXhwIjoyMDg3NzkxMjU3fQ.KtkqFcnoFU7Tf0t8FH8f7F8AlMA7Bf_yVFPVdXLzz0s"
TABLE_NAME = "nifty_indices"

INDICES = [
    "Nifty 50",
    "Nifty Smallcap 250",
    "Nifty500 Momentum 50",
    "Nifty500 Quality 50",
    "Nifty500 Value 50",
    "Nifty500 Low Volatility 50"
]

def check_all():
    print(f"{'Index Name':<30} | {'Count':<10} | {'Status'}")
    print("-" * 55)
    for index in INDICES:
        url = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=index_name&index_name=eq.{index.replace(' ', '%20')}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Prefer": "count=exact"
        }
        r = requests.get(url, headers=headers)
        count_str = r.headers.get('Content-Range', '0-0/0').split('/')[-1]
        count = int(count_str)
        status = "OK" if count >= 5180 else "INCOMPLETE"
        print(f"{index:<30} | {count:<10} | {status}")

if __name__ == "__main__":
    check_all()
