from fastapi.testclient import TestClient
from fastapi.mock import patch, MagicMock
from app.main import app
import datetime

client = TestClient(app)

def test_dashboard_returns_html():
    with patch("app.main.get_db") as mock_get_db:
        mock_db = MagicMock()
        mock_db.__enter__ = lambda s: s
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_get_db.return_value = iter([mock_db])

        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Stock Price Dashboard" in response.text
        
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Stock Price API"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

