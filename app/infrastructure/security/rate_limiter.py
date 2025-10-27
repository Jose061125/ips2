from datetime import datetime, timedelta
from collections import defaultdict
import threading
from flask import request, abort
from functools import wraps

class RateLimiter:
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = threading.Lock()

    def is_rate_limited(self, key: str) -> bool:
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)

        with self.lock:
            self.requests[key] = [req_time for req_time in self.requests[key] 
                                if req_time > window_start]
            
            if len(self.requests[key]) >= self.max_requests:
                return True

            self.requests[key].append(now)
            return False

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        limiter = RateLimiter()
        if limiter.is_rate_limited(request.remote_addr):
            abort(429)
        return f(*args, **kwargs)
    return decorated_function