import yfinance as yf
import datetime
import logging
import sys
from app.database import SessionLocal
from app.models import StockPrice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

def fetch_prices(ticker_symbol: str, period: str = "1d") -> list[dict]:
    """
    Fetch stock price history from yfinance.
    Returns a list of dicts, one per trading day.
    """
    logger.info(f"Fetching {period} data for {ticker_symbol}")
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period=period)

    if df.empty:
        logger.warning(f"No data returned for {ticker_symbol}")
        return []

    # Convert timezone-aware index to UTC naive datetime
    if df.index.tz is not None:
        df.index = df.index.tz_convert("UTC").tz_localize(None)

    records = []
    for date, row in df.iterrows():
        records.append({
            "ticker": ticker_symbol,
            "open_price": round(float(row["Open"]), 4),
            "high_price": round(float(row["High"]), 4),
            "low_price": round(float(row["Low"]), 4),
            "close_price": round(float(row["Close"]), 4),
            "volume": int(row["Volume"]),
            "price_date": date.to_pydatetime(),
        })

    return records

def ingest(period: str = "1d"):
    db = SessionLocal()
    total_inserted = 0

    try:
        for symbol in TICKERS:
            try:
                records = fetch_prices(symbol, period=period)
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
                continue

            for r in records:
                # Avoid duplicate entries for the same ticker + date
                # Prevents running the script twice in one day from creating duplicate rows - Idempotency
                exists = db.query(StockPrice).filter_by(
                    ticker=r["ticker"],
                    price_date=r["price_date"]
                ).first()

                if not exists:
                    db.add(StockPrice(**r))
                    total_inserted += 1

        db.commit()
        logger.info(f"Ingestion complete. Inserted {total_inserted} records.")

    except Exception as e:
        # If anything goes wrong, roll back the transaction to avoid partial data being saved
        db.rollback()
        logger.error(f"Ingestion failed, rolled back: {e}")
        sys.exit(1) # Github Actions will marks the job as failed

    finally:
        db.close()

if __name__ == "__main__":
    ingest(period="5d")  # backfill last 5 days on manual runs