from app.websocket_client import WebSocketManager
import time

def test_websocket_receives_data():
    manager = WebSocketManager("btcusdt")
    manager.start()
    time.sleep(5)
    data = manager.get_data()
    assert len(data) > 0
    assert "price" in data[-1]
    assert "volume" in data[-1]
