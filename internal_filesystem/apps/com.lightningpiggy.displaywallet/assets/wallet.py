import _thread
import requests
import json
import ssl
import time

from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
from nostr.filter import Filter, Filters
from nostr.event import EncryptedDirectMessage
from nostr.key import PrivateKey

import mpos.apps
import mpos.time

class Wallet:

    # These values could be loading from a cache.json file at __init__
    last_known_balance = 0
    #last_known_balance_timestamp = 0

    def __init__(self):
        pass

    def __str__(self):
        if isinstance(self, LNBitsWallet):
            return "LNBitsWallet"
        elif isinstance(self, NWCWallet):
            return "NWCWallet"

    def start_refresh_balance(self, balance_updated_cb):
        _thread.stack_size(mpos.apps.good_stack_size())
        _thread.start_new_thread(self.fetch_balance_thread, (balance_updated_cb,))

    def destroy(self):
        # optional to inherit
        pass


class LNBitsWallet(Wallet):

    def __init__(self, lnbits_url, lnbits_readkey):
        super().__init__()
        self.lnbits_url = lnbits_url
        self.lnbits_readkey = lnbits_readkey

    def fetch_balance_thread(self, balance_updated_cb):
        print("fetch_balance_thread")
        walleturl = self.lnbits_url + "/api/v1/wallet"
        headers = {
            "X-Api-Key": self.lnbits_readkey,
        }
        try:
            response = requests.get(walleturl, timeout=10, headers=headers)
        except Exception as e:
            print("GET request failed:", e)
            #lv.async_call(lambda l: please_wait_label.set_text(f"Error downloading app index: {e}"), None)
        if response and response.status_code == 200:
            response_text = response.text
            print(f"Got response text: {response_text}")
            response.close()
            try:
                balance_reply = json.loads(response_text)
                print(f"Got balance: {balance_reply['balance']}")
                balance_msat = balance_reply['balance']
                self.last_known_balance = round(balance_msat / 1000)
                #self.last_known_balance_timestamp = mpos.time.epoch_seconds()
                balance_updated_cb()
            except Exception as e:
                print(f"Could not parse reponse text '{response_text}' as JSON: {e}")


class NWCWallet(Wallet):

    def __init__(self, nwc_url):
        super().__init__()
        self.nwc_url = nwc_url
        self.relay, self.wallet_pubkey, self.secret, self.lud16 = self.parse_nwc_url(nwc_url)
        self.private_key = PrivateKey(bytes.fromhex(self.secret))
        self.relay_manager = RelayManager()
        self.relay_manager.add_relay(self.relay)
        self.connected = False

    def destroy(self):
        self.relay_manager.close_connections()

    def fetch_balance_thread(self, balance_updated_cb) :
        # make sure connected to relay (otherwise connect)
        if self.relay_manager.relays[self.relay].connected != True:
            print(f"DEBUG: Opening relay connections")
            self.relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE})
            self.connected = False
            for _ in range(20):
                time.sleep(0.5)
                if self.relay_manager.relays[self.relay].connected is True:
                    self.connected = True
                    break
                print("Waiting for relay connection...")
        if not self.connected:
            print("Failed to connect, aborting...")
            return
        # Set up subscription to receive response
        self.subscription_id = "nwc_balance_" + str(round(time.time()))
        print(f"DEBUG: Setting up subscription with ID: {self.subscription_id}")
        self.filters = Filters([Filter(
            kinds=[23195],  # NWC replies
            authors=[self.wallet_pubkey],
            pubkey_refs=[self.private_key.public_key.hex()]
        )])
        print(f"DEBUG: Subscription filters: {self.filters.to_json_array()}")
        self.relay_manager.add_subscription(self.subscription_id, self.filters)
        time.sleep(1)
        # Create get_balance request
        balance_request = {
            "method": "get_balance",
            "params": {}
        }
        print(f"DEBUG: Created balance request: {balance_request}")
        print(f"DEBUG: Creating encrypted DM to wallet pubkey: {self.wallet_pubkey}")
        dm = EncryptedDirectMessage(
            recipient_pubkey=self.wallet_pubkey,
            cleartext_content=json.dumps(balance_request)
        )
        print(f"DEBUG: Signing DM {json.dumps(dm)} with private key")
        self.private_key.sign_event(dm) # sign also does encryption if it's a encrypted dm
        print(f"DEBUG: DM created with ID: {dm.id}")
        # Publish request
        print(f"DEBUG: Publishing subscription request")
        request_message = [ClientMessageType.REQUEST, self.subscription_id]
        request_message.extend(self.filters.to_json_array())
        self.relay_manager.publish_message(json.dumps(request_message))
        print(f"DEBUG: Publishing encrypted DM")
        self.relay_manager.publish_event(dm)
        # only accept events after the time it was published
        after_time = mpos.time.epoch_seconds()
        after_time -= 60 # go back a bit because server clocks might be drifting
        print(f"will only consider events after {after_time}")

        # Wait for response
        print(f"DEBUG: Waiting for response...")
        print(f"starting at {time.localtime()}")
        start_time = mpos.time.epoch_seconds()
        balance = None
        while mpos.time.epoch_seconds() - start_time < 60 * 2:
            while self.relay_manager.message_pool.has_events():
                print(f"DEBUG: Event received from message pool")
                event_msg = self.relay_manager.message_pool.get_event()
                event_created_at = event_msg.event.created_at
                print(f"Received at {time.localtime()} a message with timestamp {event_created_at}")
                #if event_created_at < after_time:
                #    print("Skipping event because it's too old!")
                #    continue
                #print(f"event_msg content {event_msg.event.content}")
                try:
                    #print(f"DEBUG: Decrypting event from public_key: {event_msg.event.public_key}")
                    decrypted_content = self.private_key.decrypt_message(
                        event_msg.event.content,
                        event_msg.event.public_key
                    )
                    print(f"DEBUG: Decrypted content: {decrypted_content}")
                    response = json.loads(decrypted_content)
                    print(f"DEBUG: Parsed response: {response}")
                    self.last_known_balance = round(int(response["result"]["balance"]) / 1000)
                    print(f"Got balance: {self.last_known_balance}")
                    balance_updated_cb()
                    break
                except Exception as e:
                    print(f"DEBUG: Error processing response: {e}")
            if balance is not None:
                break
            time.sleep(1)

    def parse_nwc_url(self, nwc_url):
        """Parse Nostr Wallet Connect URL to extract pubkey, relay, secret, and lud16."""
        print(f"DEBUG: Starting to parse NWC URL: {nwc_url}")
        try:
            # Remove 'nostr+walletconnect://' or 'nwc:' prefix
            if nwc_url.startswith('nostr+walletconnect://'):
                print(f"DEBUG: Removing 'nostr+walletconnect://' prefix")
                nwc_url = nwc_url[22:]
            elif nwc_url.startswith('nwc:'):
                print(f"DEBUG: Removing 'nwc:' prefix")
                nwc_url = nwc_url[4:]
            else:
                print(f"DEBUG: No recognized prefix found in URL")
                raise ValueError("Invalid NWC URL: missing 'nostr+walletconnect://' or 'nwc:' prefix")
            print(f"DEBUG: URL after prefix removal: {nwc_url}")
            # Split into pubkey and query params
            parts = nwc_url.split('?')
            pubkey = parts[0]
            print(f"DEBUG: Extracted pubkey: {pubkey}")
            # Validate pubkey (should be 64 hex characters)
            if len(pubkey) != 64 or not all(c in '0123456789abcdef' for c in pubkey):
                raise ValueError("Invalid NWC URL: pubkey must be 64 hex characters")
            # Extract relay, secret, and lud16 from query params
            relay = None
            secret = None
            lud16 = None
            if len(parts) > 1:
                print(f"DEBUG: Query parameters found: {parts[1]}")
                params = parts[1].split('&')
                for param in params:
                    if param.startswith('relay='):
                        relay = param[6:] # TODO: urldecode because the relay might have %3A%2F%2F etc
                        print(f"DEBUG: Extracted relay: {relay}")
                    elif param.startswith('secret='):
                        secret = param[7:]
                        print(f"DEBUG: Extracted secret: {secret}")
                    elif param.startswith('lud16='):
                        lud16 = param[6:]
                        print(f"DEBUG: Extracted lud16: {lud16}")
            else:
                print(f"DEBUG: No query parameters found")
            if not pubkey or not relay or not secret:
                raise ValueError("Invalid NWC URL: missing required fields (pubkey, relay, or secret)")
            # Validate secret (should be 64 hex characters)
            if len(secret) != 64 or not all(c in '0123456789abcdef' for c in secret):
                raise ValueError("Invalid NWC URL: secret must be 64 hex characters")
            print(f"DEBUG: Parsed NWC data - Relay: {relay}, Pubkey: {pubkey}, Secret: {secret}, lud16: {lud16}")
            return relay, pubkey, secret, lud16
        except Exception as e:
            print(f"DEBUG: Error parsing NWC URL: {e}")

