import requests

def fetch_strategy_indices():
    url = "https://www.niftyindices.com/BackEndDataLibrary/getHistoricalIndexNameByType"
    headers = {
        "Referer": "https://www.niftyindices.com/reports/historical-data",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {"IndexType": "Strategy Indices"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            indices = response.json()
            print("Found indices:")
            for idx in indices:
                name = idx['IndexName']
                print(f"'{name}'")
        else:
            print(f"Failed to fetch: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_strategy_indices()
