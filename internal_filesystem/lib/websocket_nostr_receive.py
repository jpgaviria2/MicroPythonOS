import json
import ssl
import time
import _thread

from nostr.filter import Filter, Filters
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType

#filters = Filters([Filter(authors=[<a nostr pubkey in hex>], kinds=[EventKind.TEXT_NOTE])])
#filters = Filters([Filter(authors="04c915daefee38317fa734444acee390a8269fe5810b2241e5e6dd343dfbecc9", kinds=[EventKind.TEXT_NOTE])])
#timestamp = round(time.time()-50)
#timestamp = round(time.time()) # going for zero events to check memory use

timetogoback = 100

import sys
if sys.platform == "esp32":
    # on esp32, it needs this correction:
    timestamp = time.time() + 946684800 - timetogoback
else:
    timestamp = round(time.time()-timetogoback)
    #timestamp = round(time.time()-1000)
    #timestamp = round(time.time()-5000)

#filters = Filters([Filter(authors="04c915daefee38317fa734444acee390a8269fe5810b2241e5e6dd343dfbecc9", kinds=[9735], since=timestamp)])
filters = Filters([Filter(kinds=[9735], since=timestamp)])

subscription_id = "test" + str(round(time.time()))
request = [ClientMessageType.REQUEST, subscription_id]
json.dumps(request)
request.extend(filters.to_json_array())
message = json.dumps(request)
# ["REQ", "ihopethisworks3", {"kinds": [1], "authors": "04c915daefee38317fa734444acee390a8269fe5810b2241e5e6dd343dfbecc9"}]
print(f"sending this: {message}")

def printevents():
    import micropython
    print(f"at the start, thread stack used: {micropython.stack_use()}")
    print("relaymanager")
    relay_manager = RelayManager()
    time.sleep(3)
    #relay_manager.add_relay("wss://nostr-pub.wellorder.net")
    print("relaymanager adding")
    relay_manager.add_relay("wss://relay.damus.io")
    time.sleep(3)
    print("relaymanager subscribing")
    relay_manager.add_subscription(subscription_id, filters)
    time.sleep(3) # allow the connections to open
    print("opening connections") # after this, CPU usage goes high and stays there
    relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
    time.sleep(2) # allow the connections to open
    print("publishing:")
    relay_manager.publish_message(message)
    time.sleep(2) # allow the messages to send
    print("printing events:")
    #while relay_manager.message_pool.has_events():
    # allowing 30 seconds for stuff to come in...
    for _ in range(30):
        time.sleep(1)
        print(".")
        try:
            event_msg = relay_manager.message_pool.get_event()
            print(f"event_msg: pubkey: {event_msg.event.public_key} created_at {event_msg.event.created_at}")
        except Exception as e:
            print(f"pool.get_event() got error: {e}")
    print("30 seconds passed, closing:")
    relay_manager.close_connections()

# new thread so REPL stays available
# 12KB crashes here:
# opening connections
# [DEBUG 408724546] Starting run_forever
# [DEBUG 408724546] Starting _async_main
# [DEBUG 408724546] Reconnect interval set to 0s
# [DEBUG 408724546] Started callback processing task
# [DEBUG 408724546] Main loop iteration: self.running=True
# [DEBUG 408724546] Connecting to wss://relay.damus.io
# [DEBUG 408724547] Using SSL with no certificate verification
# 24KB is fine
# somehow, if I run this in a thread, I get: can't create thread" at File "/lib/nostr/relay_manager.py", line 48, in open_connections
# tried stack sizes from 18KB up to 32KB
#_thread.stack_size(48*1024)
#_thread.start_new_thread(printevents, ())
printevents()


#import gc
#for _ in range(50):
#    collect = gc.collect()
#    print(f"MEMFREE: {gc.mem_free()}")
#    time.sleep(1)
