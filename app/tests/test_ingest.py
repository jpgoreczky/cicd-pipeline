from unittest.mock import patch, MagicMock
import pandas as pd
import datetime
from app.ingest import fetch_prices

def make_mock_df():
    dates = pd.to_datetime(["2024-01-15", "2024-01-16"])
    df = pd.DataFrame({
        "Open":   [150.0, 151.0],
        "High":   [155.0, 156.0],
        "Low":    [149.0, 150.0],
        "Close":  [153.0, 154.0],
        "Volume": [1000000, 1100000],
        "Dividends": [0.0, 0.0],
        "Stock Splits": [0.0, 0.0],
    }, index=dates)
    df.index.name = "Date"
    return df

# patch replaces the real yfinance.Ticker with a mock object for the duration of the test and never makes real API calls to yfinance. 
@patch("app.ingest.yf.Ticker")
def test_fetch_prices_returns_correct_records(mock_ticker_class):
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = make_mock_df()
    mock_ticker_class.return_value = mock_ticker

    results = fetch_prices("AAPL", period="5d")

    assert len(results) == 2
    assert results[0]["ticker"] == "AAPL"
    assert results[0]["close_price"] == 153.0
    assert results[1]["close_price"] == 154.0

@patch("app.ingest.yf.Ticker")
def test_fetch_prices_handles_empty_response(mock_ticker_class):
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = pd.DataFrame()
    mock_ticker_class.return_value = mock_ticker

    results = fetch_prices("FAKE", period="1d")
    assert results == []