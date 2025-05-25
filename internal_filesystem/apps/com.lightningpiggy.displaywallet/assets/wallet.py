import _thread
import requests
import json

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


class LNBitsWallet(Wallet):

    def __init__(self, lnbits_url, lnbits_readkey):
        super().__init__()
        self.lnbits_url = lnbits_url
        self.lnbits_readkey = lnbits_readkey

    def fetch_balance_thread(self, lnbits_url, lnbits_readkey):
        print("fetch_balance_thread")
        walleturl = lnbits_url + "/api/v1/wallet"
        headers = {
            "X-Api-Key": lnbits_readkey,
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
            except Exception as e:
                print(f"Could not parse reponse text '{response_text}' as JSON: {e}")

    def start_refresh_balance(self):
        _thread.stack_size(mpos.apps.good_stack_size())
        _thread.start_new_thread(self.fetch_balance_thread, (self.lnbits_url, self.lnbits_readkey))

class NWCWallet(Wallet):

    def __init__(self, nwc_url):
        super().__init__()
        self.nwc_url = nwc_url
        nwc_data = parse_nwc_url(nwc_url)
        self.relay = nwc_data['relay']
        self.wallet_pubkey = nwc_data['pubkey']
        self.secret = nwc_data['secret']
        self.lud16 = nwc_data['lud16']
        print(f"DEBUG: Parsed NWC data - Relay: {relay}, Pubkey: {wallet_pubkey}, Secret: {secret}, lud16: {lud16}")
        # TODO: open connection to relay, subscribe to updates

    def start_refresh_balance(self) :
        # TODO: make sure connected to relay (otherwise connect) and fetch balance
        pass

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
    
            return {
                'relay': relay,
                'pubkey': pubkey,
                'secret': secret,
                'lud16': lud16
            }
        except Exception as e:
            print(f"DEBUG: Error parsing NWC URL: {e}")
            sys.exit(1)

