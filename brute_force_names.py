from nsepython import index_history
import time

def try_symbol(base_name):
    # Base: NIFTY100 QUALITY 30 or NIFTY200 MOMENTUM 30
    variants = [
        base_name,
        base_name.replace("NIFTY", "NIFTY "),
        base_name.replace("NIFTY", "Nifty "),
        base_name.replace("NIFTY", "Nifty").replace(" ", ""), # Nifty100Quality30
        base_name.replace("NIFTY", "Nifty") # Nifty100 QUALITY 30
    ]
    # Add Title Case versions
    variants += [v.title() for v in variants]
    
    # Clean duplicates
    variants = list(dict.fromkeys(variants))
    
    for v in variants:
        print(f"Trying '{v}'...")
        try:
            df = index_history(v, "01-Jan-2024", "28-Feb-2026")
            if df is not None and not df.empty:
                print(f"Success! {v}")
                return v
        except:
            pass
        time.sleep(0.5)
    return None

SYMBOLS = ["NIFTY100 QUALITY 30", "NIFTY100 LOW VOLATILITY 30", "NIFTY200 MOMENTUM 30"]
for s in SYMBOLS:
    res = try_symbol(s)
    if res:
        print(f"FINAL SYMBOL FOR {s}: {res}")
    else:
        print(f"COULD NOT FIND SYMBOL FOR {s}")
