import time
from fastapi import Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Limits requests per IP within a given time window.
    """
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        now = int(time.time())
        window_start = now - self.window

        if ip not in self.requests:
            self.requests[ip] = []
        self.requests[ip] = [ts for ts in self.requests[ip] if ts > window_start]

        if len(self.requests[ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"error": "Too Many Requests", "message": "Rate limit exceeded"},
            )

        self.requests[ip].append(now)

        return await call_next(request)
