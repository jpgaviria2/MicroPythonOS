import _thread

class Thread:
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        self.target = target
        self.args = args
        self.kwargs = {} if kwargs is None else kwargs

    def start(self):
        _thread.start_new_thread(self.run, ())

    def run(self):
        self.target(*self.args, **self.kwargs)


class Lock:
    def __init__(self):
        self._lock = _thread.allocate_lock() 

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
