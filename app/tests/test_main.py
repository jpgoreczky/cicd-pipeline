from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.database import get_db
import datetime

client = TestClient(app)

def test_dashboard_returns_html():
    # Build a fake db session that returns mock stock data
    mock_row = MagicMock()
    mock_row.ticker = "AAPL"
    mock_row.close_price = 189.50
    mock_row.open_price = 187.00
    mock_row.high_price = 191.00
    mock_row.low_price = 186.50
    mock_row.volume = 52000000
    mock_row.price_date = datetime.datetime(2024, 1, 15)

    mock_db = MagicMock()
    mock_db.query.return_value.group_by.return_value.subquery.return_value = MagicMock()
    mock_db.query.return_value.join.return_value.order_by.return_value.all.return_value = [mock_row]
    mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.first.return_value = None

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Stock Price Dashboard" in response.text
        assert "AAPL" in response.text
    finally:
        app.dependency_overrides.clear()

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Stock Price API"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

