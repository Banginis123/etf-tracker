import time
from scheduler import check_etf_prices

INTERVAL_SECONDS = 60 * 15  # kas 15 min

print("🚀 ETF scheduler paleistas")

while True:
    try:
        check_etf_prices()
    except Exception as e:
        print(f"❌ Scheduler klaida: {e}")

    print(f"⏳ Laukiam {INTERVAL_SECONDS // 60} min...\n")
    time.sleep(INTERVAL_SECONDS)
