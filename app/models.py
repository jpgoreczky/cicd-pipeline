from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base
import datetime


# Maps to a table 'stock_prices' in Postgres
# Each 'Column' becomes a column in the table
# 'index=True' tells Postgres to build an index on that colomn,
# which makes queries filtering by 'ticker' faster.
# 'price_date' date the the stock market was open and this price is recorded
# 'fetched_at' time the app fetched from yfinance
class StockPrice(Base):
    __tablename__ = "stock_prices"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    price_date = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)