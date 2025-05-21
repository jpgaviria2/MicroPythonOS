
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

#wsapp = websocket.WebSocketApp("wss://echo.websocket.events", on_message=on_message, on_ping=on_ping, on_pong=on_pong, on_error=on_error)

wsapp = websocket.WebSocketApp("wss://relay.damus.io", on_message=on_message, on_ping=on_ping, on_pong=on_pong, on_error=on_error)

#wsapp = websocket.WebSocketApp("wss://relay.primal.net", on_message=on_message, on_ping=on_ping, on_pong=on_pong, on_error=on_error)


def stress_test_thread():
    print("before run_forever")
    #wsapp.run_forever(ping_interval=30, ping_timeout=10)
    #wsapp.run_forever(ping_interval=300, ping_timeout=10, ping_payload="This is an optional ping payload")
    wsapp.run_forever()
    print("after run_forever")

_thread.stack_size(32*1024)
_thread.start_new_thread(stress_test_thread, ())

time.sleep(5)
print("sending it")
# nothing:
#wsapp.send_text('["REQ", "ihopethisworks3", {"kinds": [1], "authors": "04c915daefee38317fa734444acee390a8269fe5810b2241e5e6dd343dfbecc9"}]')
#wsapp.send_text('["REQ", "ihopethisworks3", {"kinds": [1] }]')
# this worked at some point:
#wsapp.send_text('["REQ","index3",{"kinds":[9735]}]')
#wsapp.send_text('["REQ","index3",{"kinds":[9735], "since": 1745086888}]')
tosend = '["REQ","index3",{"kinds":[9735], "since": '
tosend += str(round(time.time()-1000))
tosend += '}]'
print(f"sending: {tosend}")
wsapp.send_text(tosend)
#1745086888
#["REQ","index",{"kinds":[9735]}]


print("waiting 30 seconds...")
time.sleep(30)
#print("sending again")
#wsapp.send_text('again')


time.sleep(25)
#print("sending more")
#wsapp.send_text('more')

wsapp.close()


