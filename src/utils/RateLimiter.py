import  time
from multiprocessing import Process, Queue,Lock

class RateLimiter:
    #Simple rate limiter to be polite to websites
    def __init__(self, max_requests_per_second: float = 1.0):
        self.max_requests_per_second = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0
        self.lock = None  # Initialize lock lazily

    def _get_lock(self):
        if self.lock is None:
            self.lock = Lock()
        return self.lock

    def wait_if_needed(self):
        lock = self._get_lock()
        with lock:
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                time.sleep(sleep_time)
            self.last_request_time = time.time()