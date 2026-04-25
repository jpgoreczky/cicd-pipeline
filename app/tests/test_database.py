import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, StockPrice
import datetime

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")    # creates a tempory in memory database that exists only for the duration of the test
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_insert_and_query_stock_price(db_session):
    record = StockPrice(
        ticker="AAPL",
        open_price=150.0,
        high_price=155.0,
        low_price=149.0,
        close_price=153.0,
        volume=1000000,
        price_date=datetime.datetime(2024, 1, 15)
    )
    db_session.add(record)
    db_session.commit()

    result = db_session.query(StockPrice).filter_by(ticker="AAPL").first()
    assert result is not None
    assert result.close_price == 153.0