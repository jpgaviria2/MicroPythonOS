import time

def epoch_seconds():
    import sys
    if sys.platform == "esp32":
        # on esp32, it needs this correction:
        return time.time() + 946684800
    else:
        return round(time.time())
    
