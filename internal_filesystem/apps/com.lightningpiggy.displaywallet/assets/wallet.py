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
        self.keep_running = True

    def __str__(self):
        if isinstance(self, LNBitsWallet):
            return "LNBitsWallet"
        elif isinstance(self, NWCWallet):
            return "NWCWallet"

    # Need callbacks for:
    #    - started (so the user can show the UI) 
    #    - stopped (so the user can delete/free it)
    #    - error (so the user can show the error)
    #    - balance
    #    - transactions
    def start(self, balance_updated_cb):
        self.keep_running = True
        _thread.stack_size(mpos.apps.good_stack_size())
        _thread.start_new_thread(self.wallet_manager_thread, (balance_updated_cb,))

    def stop(self):
        self.keep_running = False

    def is_running(self):
        return self.keep_running

class LNBitsWallet(Wallet):

    def __init__(self, lnbits_url, lnbits_readkey):
        super().__init__()
        self.lnbits_url = lnbits_url
        self.lnbits_readkey = lnbits_readkey

    def wallet_manager_thread(self, balance_updated_cb):
        print("wallet_manager_thread")
        while self.keep_running:
            try:
                self.last_known_balance = fetch_balance()
                balance_updated_cb()
                # TODO: if the balance changed, then re-list transactions
            except Exception as e:
                print(f"WARNING: fetch_balance got exception {e}, ignorning.")
            print("Sleeping a while before re-fetching balance...")
            time.sleep(60)
        print("wallet_manager_thread stopping")

    def fetch_balance():
        walleturl = self.lnbits_url + "/api/v1/wallet"
        headers = {
            "X-Api-Key": self.lnbits_readkey,
        }
        try:
            response = requests.get(walleturl, timeout=10, headers=headers)
        except Exception as e:
            print("fetch_balance: get request failed:", e)
        if response and response.status_code == 200:
            response_text = response.text
            print(f"Got response text: {response_text}")
            response.close()
            try:
                balance_reply = json.loads(response_text)
                print(f"Got balance: {balance_reply['balance']}")
                balance_msat = balance_reply['balance']
                return round(balance_msat / 1000)
            except Exception as e:
                print(f"Could not parse reponse text '{response_text}' as JSON: {e}")
                raise e


class NWCWallet(Wallet):

    def __init__(self, nwc_url):
        super().__init__()
        self.nwc_url = nwc_url
        self.connected = False

    def wallet_manager_thread(self, balance_updated_cb):
        self.relay, self.wallet_pubkey, self.secret, self.lud16 = self.parse_nwc_url(self.nwc_url)
        self.private_key = PrivateKey(bytes.fromhex(self.secret))
        self.relay_manager = RelayManager()
        self.relay_manager.add_relay(self.relay)

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
            print("ERROR: could not connect to NWC relay {self.relay}, aborting...")
            # TODO: call an error callback to notify the user
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
        print(f"DEBUG: Publishing subscription request")
        request_message = [ClientMessageType.REQUEST, self.subscription_id]
        request_message.extend(self.filters.to_json_array())
        self.relay_manager.publish_message(json.dumps(request_message))
        print(f"DEBUG: Publishing encrypted DM")
        self.relay_manager.publish_event(dm)

        print(f"DEBUG: Waiting for incoming NWC events...")
        while self.keep_running:
            if self.relay_manager.message_pool.has_events():
                print(f"DEBUG: Event received from message pool")
                event_msg = self.relay_manager.message_pool.get_event()
                event_created_at = event_msg.event.created_at
                print(f"Received at {time.localtime()} a message with timestamp {event_created_at}")
                try:
                    decrypted_content = self.private_key.decrypt_message(
                        event_msg.event.content,
                        event_msg.event.public_key
                    )
                    print(f"DEBUG: Decrypted content: {decrypted_content}")
                    response = json.loads(decrypted_content)
                    print(f"DEBUG: Parsed response: {response}")
                    if response["result"]:
                        if response["result"]["balance"]:
                            self.last_known_balance = round(int(response["result"]["balance"]) / 1000)
                            print(f"Got balance: {self.last_known_balance}")
                            # TODO: if balance changed, then update list of transactions
                            balance_updated_cb()
                        elif response["result"]["transactions"]:
                            print("TODO: Response contains transactions!")
                        else:
                            print("Unsupported response, ignoring.")
                    else:
                        print("Event doesn't contain result, ignoring.")
                except Exception as e:
                    print(f"DEBUG: Error processing response: {e}")
            time.sleep(1)

        print("NWCWallet: manage_wallet_thread stopping, closing connections...")
        self.relay_manager.close_connections()


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
            # TODO: urldecode because the relay might have %3A%2F%2F etc
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
                        relay = param[6:]
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

