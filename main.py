import logging
import requests
import pandas as pd
from datetime import datetime, timezone
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def fetch_prices():

    params = {"ids": "bitcoin,ethereum", "vs_currencies": "usd"}

    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price", params=params, timeout=10)
        response.raise_for_status()
        logger.info("API request successful.")
        data = response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise SystemExit(1)
    return data


def build_rows(data):   
    rows = []
    for coin, info in data.items():
        price = info.get("usd", None)
        if price is None:
            logger.warning(f"Price for {coin} is missing.")
            continue
        rows.append({"coin": coin, "price_usd": price})
    logger.info(f"Get coins amount: {len(rows)}")
    return rows


def save_to_csv(rows):
    df = pd.DataFrame(rows)
    df["timestamp"] = datetime.now(timezone.utc).isoformat()
    file_exists = os.path.exists("prices.csv")
    df.to_csv("prices.csv", mode="a", header=not file_exists, index=False)
    logger.info("Data saved to CSV.")


if __name__ == "__main__":
    data = fetch_prices()
    rows = build_rows(data)
    if rows != []:
        save_to_csv(rows)
    else:
        logger.warning("No data to save.")
    logger.info("Process completed successfully.")
