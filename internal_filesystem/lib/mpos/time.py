import time

def epoch_seconds():
    import sys
    if sys.platform == "esp32":
        # on esp32, it needs this correction:
        return time.time() + 946684800
    else:
        return round(time.time())

def sync_time():
    import ntptime
    print("Synchronizing clock...")
    # Set the NTP server and sync time
    ntptime.host = 'pool.ntp.org'  # Set NTP server
    try:
        print('Syncing time with', ntptime.host)
        ntptime.settime()  # Fetch and set time (in UTC)
        print('Time synced successfully')
    except Exception as e:
        print('Failed to sync time:', e)
