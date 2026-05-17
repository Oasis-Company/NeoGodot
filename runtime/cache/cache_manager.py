import hashlib
import pickle
import time
import asyncio
from collections import OrderedDict
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generic, Optional, Tuple, TypeVar, Coroutine, Union
from inspect import iscoroutinefunction

T = TypeVar('T')


@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: float


class LRUCache(Generic[T]):
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry[T]] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._lock = asyncio.Lock()

    def get(self, key: str) -> Optional[T]:
        if key not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[key]
        if self._is_expired(entry):
            self._remove(key)
            return None

        self._cache.move_to_end(key)
        self._hits += 1
        return entry.value

    def set(self, key: str, value: T, ttl: Optional[float] = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        expires_at = float('inf') if ttl is None else time.time() + ttl

        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.max_size:
                self._evict_oldest()

        self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str) -> bool:
        if key in self._cache:
            self._remove(key)
            return True
        return False

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def _is_expired(self, entry: CacheEntry[T]) -> bool:
        return time.time() > entry.expires_at

    def _remove(self, key: str) -> None:
        del self._cache[key]

    def _evict_oldest(self) -> None:
        self._cache.popitem(last=False)
        self._evictions += 1

    def stats(self) -> dict[str, int]:
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total": total,
            "hit_rate": hit_rate,
            "evictions": self._evictions,
            "size": len(self._cache),
            "max_size": self.max_size
        }

    async def aget(self, key: str) -> Optional[T]:
        async with self._lock:
            return self.get(key)

    async def aset(self, key: str, value: T, ttl: Optional[float] = None) -> None:
        async with self._lock:
            self.set(key, value, ttl)

    async def adelete(self, key: str) -> bool:
        async with self._lock:
            return self.delete(key)

    async def aclear(self) -> None:
        async with self._lock:
            self.clear()

    def __contains__(self, key: str) -> bool:
        if key not in self._cache:
            return False
        if self._is_expired(self._cache[key]):
            self._remove(key)
            return False
        return True

    def __len__(self) -> int:
        self._cleanup()
        return len(self._cache)

    def _cleanup(self) -> None:
        expired_keys = [k for k, v in self._cache.items() if self._is_expired(v)]
        for k in expired_keys:
            self._remove(k)


def generate_cache_key(
    func_name: str,
    args: Tuple[Any, ...],
    kwargs: dict[str, Any],
    typed: bool = False
) -> str:
    key_parts = [func_name]

    for arg in args:
        key_parts.append(_hashable_repr(arg, typed))

    sorted_kwargs = sorted(kwargs.items())
    for k, v in sorted_kwargs:
        key_parts.append(str(k))
        key_parts.append(_hashable_repr(v, typed))

    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def _hashable_repr(obj: Any, typed: bool) -> str:
    try:
        repr_str = repr(obj)
    except (ValueError, TypeError):
        try:
            repr_str = pickle.dumps(obj).hex()
        except (ValueError, TypeError, pickle.PicklingError):
            repr_str = str(id(obj))

    if typed:
        return f"{type(obj).__name__}:{repr_str}"
    return repr_str


_default_cache: Optional[LRUCache[Any]] = None


def get_default_cache() -> LRUCache[Any]:
    global _default_cache
    if _default_cache is None:
        _default_cache = LRUCache()
    return _default_cache


def cached(
    cache: Optional[LRUCache[Any]] = None,
    ttl: Optional[float] = None,
    typed: bool = False,
    key_prefix: str = ""
) -> Callable:
    cache_obj = cache if cache is not None else get_default_cache()

    def decorator(func: Callable) -> Callable:
        if iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                key = f"{key_prefix}{generate_cache_key(func.__qualname__, args, kwargs, typed)}"
                result = await cache_obj.aget(key)
                if result is not None:
                    return result
                result = await func(*args, **kwargs)
                await cache_obj.aset(key, result, ttl)
                return result
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                key = f"{key_prefix}{generate_cache_key(func.__qualname__, args, kwargs, typed)}"
                result = cache_obj.get(key)
                if result is not None:
                    return result
                result = func(*args, **kwargs)
                cache_obj.set(key, result, ttl)
                return result
            return sync_wrapper

    return decorator
