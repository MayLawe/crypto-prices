CREATE TABLE IF NOT EXISTS prices (
    id         SERIAL PRIMARY KEY,
    coin       TEXT NOT NULL,
    price_usd  NUMERIC(18, 8) NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_prices_coin_time ON prices (coin, fetched_at);