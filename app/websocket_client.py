import websocket
import json
import threading
from collections import deque
from typing import List, Dict, Any, Optional

MAX_QUEUE_SIZE = 500

class WebSocketManager:
    def __init__(self, symbol: str = "btcusdt") -> None:
        self.symbol = symbol  # <-- Store symbol here
        self.url = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
        self.queue: deque = deque(maxlen=MAX_QUEUE_SIZE)
        self.ws: Optional[websocket.WebSocketApp] = None

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        data = json.loads(message)
        self.queue.append({
            "price": float(data["p"]),
            "volume": float(data["q"]),
            "timestamp": int(data["T"]),
        })

    def on_error(self, ws: websocket.WebSocketApp, error: Any) -> None:
        print("WebSocket Error:", error)

    def on_close(self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str) -> None:
        print("WebSocket closed:", close_msg)

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        print("WebSocket connected")

    def start(self) -> None:
        def run() -> None:
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            self.ws.run_forever()
        threading.Thread(target=run, daemon=True).start()

    def get_data(self) -> List[Dict[str, Any]]:
        return list(self.queue)

    def stop(self) -> None:
        """Optional: method to stop the websocket."""
        if self.ws:
            self.ws.close()
