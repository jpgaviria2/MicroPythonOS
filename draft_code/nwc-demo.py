import json
import ssl
import time
import sys
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
from nostr.filter import Filter, Filters
from nostr.event import EncryptedDirectMessage
from nostr.key import PrivateKey

def parse_nwc_url(nwc_url):
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

        return {
            'relay': relay,
            'pubkey': pubkey,
            'secret': secret,
            'lud16': lud16
        }
    except Exception as e:
        print(f"DEBUG: Error parsing NWC URL: {e}")
        sys.exit(1)

def get_balance(nwc_url):
    """Get balance using Nostr Wallet Connect."""
    print(f"DEBUG: Starting get_balance with NWC URL: {nwc_url}")
    # Parse NWC URL
    nwc_data = parse_nwc_url(nwc_url)
    relay = nwc_data['relay']
    wallet_pubkey = nwc_data['pubkey']
    secret = nwc_data['secret']
    lud16 = nwc_data['lud16']
    print(f"DEBUG: Parsed NWC data - Relay: {relay}, Pubkey: {wallet_pubkey}, Secret: {secret}, lud16: {lud16}")

    # Initialize private key from secret (assuming it's a hex key)
    try:
        #print(f"DEBUG: Initializing private key from secret")
        private_key = PrivateKey(bytes.fromhex(secret))
        print(f"DEBUG: Private key initialized, public key: {private_key.public_key.hex()}")
    except Exception as e:
        print(f"DEBUG: Error initializing private key: {e}")
        sys.exit(1)

    # Create get_balance request
    balance_request = {
        "method": "get_balance",
        "params": {}
    }
    print(f"DEBUG: Created balance request: {balance_request}")

    #balance_request_string = json.dumps(balance_request)
    #encrypted = private_key.encrypt_message(balance_request_string, wallet_pubkey)
    #print(f"\n\n\nencryption returned: {encrypted}")
    #decrypted = private_key.decrypt_message(encrypted, wallet_pubkey)
    #print(f"\n\n\ndecryption returned: {decrypted}\n\n\n")

    #decrypted = private_key.decrypt_message(encrypted, wallet_pubkey)
    #print(f"\n\n\ndecryption from nak returned: {decrypted}\n\n\n")
    # padding error


    # Create encrypted DM with the balance request
    print(f"DEBUG: Creating encrypted DM to wallet pubkey: {wallet_pubkey}")
    dm = EncryptedDirectMessage(
        recipient_pubkey=wallet_pubkey,
        cleartext_content=json.dumps(balance_request)
    )
    
    
    print(f"DEBUG: Signing DM {json.dumps(dm)} with private key")
    private_key.sign_event(dm) # sign also does encryption if it's a encrypted dm
    print(f"DEBUG: DM created with ID: {dm.id}")

    # Set up relay manager
    print(f"DEBUG: Setting up relay manager with relay: {relay}")
    relay_manager = RelayManager()
    relay_manager.add_relay(relay)
    print(f"DEBUG: Opening relay connections")
    relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE})
    time.sleep(2)  # Allow connections to open

    # Check for relay connection notices
    print(f"DEBUG: Checking for relay notices")
    while relay_manager.message_pool.has_notices():
        notice = relay_manager.message_pool.get_notice()
        print(f"DEBUG: Relay notice: {notice.content}")

    # Set up subscription to receive response
    subscription_id = "nwc_balance_" + str(round(time.time()))
    #print(f"DEBUG: Setting up subscription with ID: {subscription_id}")
    filters = Filters([Filter(
        kinds=[23195],  # NWC replies
        authors=[wallet_pubkey],
        pubkey_refs=[private_key.public_key.hex()]
    )])
    #print(f"DEBUG: Subscription filters: {filters.to_json_array()}")
    relay_manager.add_subscription(subscription_id, filters)

    # Publish request
    print(f"DEBUG: Publishing subscription request")
    request_message = [ClientMessageType.REQUEST, subscription_id]
    request_message.extend(filters.to_json_array())
    relay_manager.publish_message(json.dumps(request_message))
    print(f"DEBUG: Publishing encrypted DM")
    relay_manager.publish_event(dm)
    # only accept events after the time it was published
    after_time = time.time()
    if sys.platform == "esp32":
        # on esp32, it needs this correction:
        after_time += 946684800
    after_time -= 60 # go back a bit because server clocks might be drifting
    print(f"will only consider events after {after_time}")


    # Wait for response
    print(f"DEBUG: Waiting for response...")
    print(f"starting at {time.localtime()}")
    start_time = time.time()
    balance = None
    while time.time() - start_time < 60 * 2:
        while relay_manager.message_pool.has_events():
            print(f"DEBUG: Event received from message pool")
            event_msg = relay_manager.message_pool.get_event()
            event_created_at = event_msg.event.created_at
            print(f"Received at {time.localtime()} a message with timestamp {event_created_at}")
            if event_created_at < after_time:
                print("Skipping event because it's too old!")
                continue
            #print(f"event_msg content {event_msg.event.content}")
            try:
                #print(f"DEBUG: Decrypting event from public_key: {event_msg.event.public_key}")
                decrypted_content = private_key.decrypt_message(
                    event_msg.event.content,
                    event_msg.event.public_key
                )
                print(f"DEBUG: Decrypted content: {decrypted_content}")
                response = json.loads(decrypted_content)
                print(f"DEBUG: Parsed response: {response}")
                if response.get("method") == "get_balance":
                    balance = response.get("result", {}).get("balance")
                    print(f"DEBUG: Balance found: {balance} satoshis")
                    break
            except Exception as e:
                print(f"DEBUG: Error processing response: {e}")
        if balance is not None:
            break
        time.sleep(1)
    
    print(f"finished at {time.localtime()}")

    # Close connections
    print(f"DEBUG: Closing relay connections")
    relay_manager.close_connections()

    if balance is not None:
        print(f"Balance: {balance} satoshis")
    else:
        print("No balance response received or request timed out")

# Example usage
#nwc_url = "nostr+walletconnect://b889ff5b1513b641e2a139f661a661364979c5beee91842f8f0ef42ab558e9d4?relay=wss%3A%2F%2Frelay.getalby.com/v1&secret=71a8c14c1407c113601079c4302dab36460f0ccd0ad506f1f2dc73b5100e4f3c&lud16=moritz@getalby.com"
#nwc_url = "nostr+walletconnect://b889ff5b1513b641e2a139f661a661364979c5beee91842f8f0ef42ab558e9d4?relay=wss://relay.getalby.com/v1&secret=71a8c14c1407c113601079c4302dab36460f0ccd0ad506f1f2dc73b5100e4f3c&lud16=moritz@getalby.com"
print(f"Processing NWC URL: {nwc_url}")
get_balance(nwc_url)
