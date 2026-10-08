import logging
import requests
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

def get_connection():
    conn = psycopg2.connect(
        host = os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname = os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    return conn


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


def save_to_db(rows):
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                for row in rows:
                    cur.execute("INSERT INTO prices(coin, price_usd, fetched_at) VALUES (%s,%s,%s)",
                                (row["coin"], row["price_usd"], now)
                            )
        logger.info(f"Записано {len(rows)} строк")

    finally:
        conn.close()

if __name__ == "__main__":
    data = fetch_prices()
    rows = build_rows(data)
    if rows != []:
        save_to_db(rows)
    else:
        logger.warning("No data to save.")
    logger.info("Process completed successfully.")
