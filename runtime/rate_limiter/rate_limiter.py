import time
import asyncio
from typing import Dict, Optional, Callable
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


class TokenBucket:
    def __init__(self, capacity: float, rate: float):
        self.capacity = capacity
        self.rate = rate
        self._tokens = capacity
        self._last_refill = time.time()

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
        self._last_refill = now

    def consume(self, tokens: float = 1.0) -> bool:
        self._refill()
        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False

    def get_retry_after(self, tokens: float = 1.0) -> float:
        self._refill()
        if self._tokens >= tokens:
            return 0.0
        needed = tokens - self._tokens
        return needed / self.rate


class RateLimiter:
    def __init__(
        self,
        requests_per_second: float = 10.0,
        capacity: Optional[float] = None,
        key_function: Optional[Callable[[Request], str]] = None,
    ):
        self.rate = requests_per_second
        self.capacity = capacity if capacity is not None else requests_per_second * 2
        self.key_function = key_function or self._default_key_function
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _default_key_function(request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        client = request.client
        return client.host if client else "unknown"

    async def _get_or_create_bucket(self, key: str) -> TokenBucket:
        async with self._lock:
            if key not in self._buckets:
                self._buckets[key] = TokenBucket(self.capacity, self.rate)
            return self._buckets[key]

    async def check_rate_limit(self, request: Request) -> Optional[JSONResponse]:
        key = self.key_function(request)
        bucket = await self._get_or_create_bucket(key)
        
        if not bucket.consume():
            retry_after = bucket.get_retry_after()
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "code": "RATE_LIMIT_EXCEEDED",
                    "detail": "Rate limit exceeded. Please try again later.",
                },
                headers={"Retry-After": str(int(retry_after) + 1)},
            )
        return None

    async def __call__(self, request: Request, call_next):
        error_response = await self.check_rate_limit(request)
        if error_response:
            return error_response
        return await call_next(request)
