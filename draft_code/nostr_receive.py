import json
import ssl
import time
import _thread

from nostr.filter import Filter, Filters
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType

#filters = Filters([Filter(authors=[<a nostr pubkey in hex>], kinds=[EventKind.TEXT_NOTE])])
#filters = Filters([Filter(authors=["181137054fe60df5168976311f0bf44dbe4bd4d2e0af69325dfee9fa81a8cbda"], kinds=[EventKind.TEXT_NOTE])])
#timestamp = round(time.time()-50)
#timestamp = round(time.time()) # going for zero events to check memory use

timetogoback = 1000
timetogoback = 2419200 # 28 days
timetogoback = 7776000 # 3 months

# event_msg: pubkey: 181137054fe60df5168976311f0bf44dbe4bd4d2e0af69325dfee9fa81a8cbda created_at 1745510390 with content "kind":1, Happy news! LightningPiggy is heading to
# contacts: event_msg: pubkey: 181137054fe60df5168976311f0bf44dbe4bd4d2e0af69325dfee9fa81a8cbda created_at 1746307620 with content  and kind 3 and tags [['p', '181137054fe60df5168976311f0bf44dbe4bd4d2e0af69325dfee9fa81a8cbda'], ['p', 'ffb3f96661bda0295389cfc8c8fe65332e98cc24b12bce5ca40e09af3bb0d7bf'],
# reaction: event_msg: pubkey: 181137054fe60df5168976311f0bf44dbe4bd4d2e0af69325dfee9fa81a8cbda created_at 1746307202 with content + and kind 7 and tags [['e', 'cee2aadc637f56e6f922b95898eecb2bd9b0f0f0ab2e2df6bb6d1e7830c697b0'], ['p', '3e6e0735b8a2e96f8cf663f64d04bb9cea931afcc57f5427c35bb6859e95c8a2']]
# event_msg: pubkey: 181137054fe60df5168976311f0bf44dbe4bd4d2e0af69325dfee9fa81a8cbda created_at 1742146581 with content The kWh (kilowatt-hour) was pro... nd kind 1 and tags [['p', '92cbe5861cfc5213dd89f0a6f6084486f85e6f03cfeb70a13f455938116433b8', 'wss://nostrelites.org', 'mention']]

# somehow, adding kinds breaks it?!
# ["REQ", "test1747750250", {"since": 1744011312, "kinds": [1], "authors": ["181137054fe60df5168976311f0bf44dbe4bd4d2e0af69325dfee9fa81a8cbda"]}]
# => this gives me EOSE quickly
# ["REQ", "test1747750060", {"since": 1744011312, "authors": ["181137054fe60df5168976311f0bf44dbe4bd4d2e0af69325dfee9fa81a8cbda"]}]
# this worked before, I think:
# ["REQ","index",{"kinds":[9735], "#p": ["181137054fe60df5168976311f0bf44dbe4bd4d2e0af69325dfee9fa81a8cbda"]}]

import sys
if sys.platform == "esp32":
    # on esp32, it needs this correction:
    timestamp = time.time() + 946684800 - timetogoback
else:
    timestamp = round(time.time()-timetogoback)
    #timestamp = round(time.time()-1000)
    #timestamp = round(time.time()-5000)

timestamp = 1744011312

filters = Filters([Filter(authors=["181137054fe60df5168976311f0bf44dbe4bd4d2e0af69325dfee9fa81a8cbda"], since=timestamp)])
#filters = Filters([Filter(authors=["181137054fe60df5168976311f0bf44dbe4bd4d2e0af69325dfee9fa81a8cbda"], since=timestamp, kinds=[EventKind.TEXT_NOTE] )])
#filters = Filters([Filter(authors=["04c915daefee38317fa734444acee390a8269fe5810b2241e5e6dd343dfbecc9"], kinds=[9735], since=timestamp)])
#filters = Filters([Filter(kinds=[9735], since=timestamp)])

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
    #relay_manager.add_relay("wss://nostr-pub.wellorder.net")
    print("relaymanager adding")
    relay_manager.add_relay("wss://relay.primal.net")
    #relay_manager.add_relay("wss://relay.damus.io")
    print("relaymanager subscribing")
    relay_manager.add_subscription(subscription_id, filters)
    print("opening connections") # after this, CPU usage goes high and stays there
    relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
    time.sleep(2) # allow the connections to open
    print("publishing:")
    relay_manager.publish_message(message)
    time.sleep(2) # allow the messages to send
    print("printing events:")
    #while relay_manager.message_pool.has_events():
    # allowing 30 seconds for stuff to come in...
    for _ in range(600):
        time.sleep(1)
        print("checking pool....")
        try:
            event_msg = relay_manager.message_pool.get_event()
            print(f"event_msg: pubkey: {event_msg.event.public_key} created_at {event_msg.event.created_at} with content '{event_msg.event.content}' and kind {event_msg.event.kind} and tags {event_msg.event.tags}")
        except Exception as e:
            #print(f"pool.get_event() got error: {e}")
            pass
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
#_thread.stack_size(16*1024)
#_thread.start_new_thread(printevents, ())
printevents()


#import gc
#for _ in range(50):
#    collect = gc.collect()
#    print(f"MEMFREE: {gc.mem_free()}")
#    time.sleep(1)
