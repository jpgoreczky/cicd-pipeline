from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app import database
from app.models import StockPrice
import datetime

app = FastAPI(title="Stock Price API")


@app.get("/prices/latest")
def get_latest_prices(db: Session = Depends(database.get_db)):
    """
    Returns the most recent close price for each tracked ticker.
    Uses a subquery to find the max price_date per ticker. (Greatest-n-per-group)
    """
    subquery = (
        db.query(
            StockPrice.ticker,
            func.max(StockPrice.price_date).label("max_date")
        )
        .group_by(StockPrice.ticker)
        .subquery()
    )

    results = (
        db.query(StockPrice)
        .join(subquery, (StockPrice.ticker == subquery.c.ticker) &
                        (StockPrice.price_date == subquery.c.max_date))
        .all()
    )

    return [
        {
            "ticker": r.ticker,
            "close_price": r.close_price,
            "price_date": r.price_date,
        }
        for r in results
    ]


@app.get("/prices/history")
def get_price_history(
    ticker: str = Query(..., description="Stock ticker symbol e.g. AAPL"),
    days: int = Query(30, description="Number of days of history to return"),
    db: Session = Depends(database.get_db)
):
    """
    Returns daily close prices for a given ticker over the last N days.
    """
    since = datetime.datetime.utcnow() - datetime.timedelta(days=days)

    results = (
        db.query(StockPrice)
        .filter(StockPrice.ticker == ticker.upper())
        .filter(StockPrice.price_date >= since)
        .order_by(desc(StockPrice.price_date))
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

    return [
        {"date": r.price_date, "close": r.close_price, "volume": r.volume}
        for r in results
    ]


@app.get("/prices/summary")
def get_price_summary(
    days: int = Query(30, description="Lookback window in days"),
    db: Session = Depends(database.get_db)
):
    """
    Returns min, max, avg close price per ticker over the last N days.
    This is a GROUP BY aggregation query — demonstrates SQL analytics.
    """
    since = datetime.datetime.utcnow() - datetime.timedelta(days=days)

    results = (
        db.query(
            StockPrice.ticker,
            func.min(StockPrice.close_price).label("min_close"),
            func.max(StockPrice.close_price).label("max_close"),
            func.avg(StockPrice.close_price).label("avg_close"),
            func.count(StockPrice.id).label("data_points"),
        )
        .filter(StockPrice.price_date >= since)
        .group_by(StockPrice.ticker)
        .order_by(StockPrice.ticker)
        .all()
    )

    return [
        {
            "ticker": r.ticker,
            "min_close": round(r.min_close, 2),
            "max_close": round(r.max_close, 2),
            "avg_close": round(r.avg_close, 2),
            "data_points": r.data_points,
        }
        for r in results
    ]

@app.get("/")
def read_root():
    return {"message": "Welcome to the Stock Price API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
