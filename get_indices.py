from nsepython import nse_get_index_list
import json

try:
    indices = nse_get_index_list()
    print(json.dumps(indices, indent=2))
except Exception as e:
    print(f"Error: {e}")
