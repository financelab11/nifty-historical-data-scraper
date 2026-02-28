from nsepython import *
import pandas as pd
from datetime import datetime

symbol = "Nifty500 Momentum 50"
start_date = "01-Apr-2005"
end_date = "27-Feb-2026"

try:
    # nsepython uses DD-MM-YYYY
    data = index_history(symbol, start_date, end_date)
    print(data.head())
    data.to_csv("nse_test.csv", index=False)
except Exception as e:
    print(f"Error: {e}")
