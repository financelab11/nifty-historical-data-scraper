import requests
import json
import time

url = "https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString"

headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.niftyindices.com/reports/historical-data",
    "X-Requested-With": "XMLHttpRequest"
}

def test_fetch():
    session = requests.Session()
    # 1. Get cookies from the reports page
    print("Getting cookies...")
    session.get("https://www.niftyindices.com/reports/historical-data", headers=headers)
    
    # 2. Try fetching Nifty 50 for a short period
    inner_params = {
        "name": "Nifty 50",
        "startDate": "01-Jan-2024",
        "endDate": "31-Jan-2024"
    }
    payload = {"cinfo": json.dumps(inner_params)}
    
    print(f"Fetching data for {inner_params['name']}...")
    try:
        response = session.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'd' in data:
                records = json.loads(data['d'])
                print(f"Success! Found {len(records)} records.")
                if records:
                    print(f"First record: {records[0]}")
            else:
                print(f"No 'd' key in response: {data}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_fetch()
