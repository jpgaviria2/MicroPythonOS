try:
    import _thread
except ImportError:
    _thread = None

class Lock:
    def __init__(self):
        self._lock = _thread.allocate_lock() if _thread else None

    def __enter__(self):
        if self._lock:
            self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._lock:
            self._lock.release()

    def acquire(self):
        if self._lock:
            return self._lock.acquire()
        return True

    def release(self):
        if self._lock:
            self._lock.release()
