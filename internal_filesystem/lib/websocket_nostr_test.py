from websocket import WebSocketApp

def on_message(ws, message):
    print(f"Received: {message}")

def on_open(ws):
    ws.send_text("Hello, Nostr!")

ws = WebSocketApp(
    url="wss://relay.damus.io",
    on_open=on_open,
    on_message=on_message,
    on_error=lambda ws, e: print(f"Error: {e}"),
    on_close=lambda ws, code, reason: print("Closed")
)
ws.run_forever(ping_interval=30, ping_timeout=10)
