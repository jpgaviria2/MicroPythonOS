# it's not super fast but it works!

import websocket
import _thread
import time

def on_message(wsapp, message):
    print(f"got message: {message}")

def on_ping(wsapp, message):
    print("Got a ping! A pong reply has already been automatically sent.")

def on_pong(wsapp, message):
    print("Got a pong! No need to respond")
    

def on_error(wsapp, message):
    print(f"Got error: {message}")
    

#wsapp = websocket.WebSocketApp("wss://testnet.binance.vision/ws/btcusdt@trade", on_message=on_message, on_ping=on_ping, on_pong=on_pong, on_error=on_error)

wsapp = websocket.WebSocketApp("wss://echo.websocket.events", on_message=on_message, on_ping=on_ping, on_pong=on_pong, on_error=on_error)

def stress_test_thread():
    print("before run_forever")
    wsapp.run_forever(ping_interval=15, ping_timeout=10, ping_payload="This is an optional ping payload")
    print("after run_forever")

_thread.stack_size(16*1024)
_thread.start_new_thread(stress_test_thread, ())

time.sleep(5)
print("sending ok")
wsapp.send_text('ok')


time.sleep(15)
print("sending again")
wsapp.send_text('again')


time.sleep(25)
print("sending more")
wsapp.send_text('more')

wsapp.close()


