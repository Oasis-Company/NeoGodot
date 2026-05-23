import hashlib
import pickle
import time
import asyncio
from collections import OrderedDict
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generic, Optional, Tuple, TypeVar, Coroutine, Union
from inspect import iscoroutinefunction
import logging

logger = logging.getLogger(__name__)

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


class ExactCache:
    """精确缓存：基于哈希的精确匹配缓存"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = 3600):
        self._cache = LRUCache(max_size=max_size, default_ttl=default_ttl)
    
    def _compute_key(self, data: str) -> str:
        """计算数据的哈希键"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def get(self, data: str) -> Optional[Any]:
        """获取缓存"""
        key = self._compute_key(data)
        return self._cache.get(key)
    
    def set(self, data: str, value: Any, ttl: Optional[float] = None) -> None:
        """设置缓存"""
        key = self._compute_key(data)
        self._cache.set(key, value, ttl)
    
    def delete(self, data: str) -> bool:
        """删除缓存"""
        key = self._compute_key(data)
        return self._cache.delete(key)
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
    
    def stats(self) -> dict:
        """获取统计信息"""
        return self._cache.stats()
    
    async def aget(self, data: str) -> Optional[Any]:
        """异步获取缓存"""
        key = self._compute_key(data)
        return await self._cache.aget(key)
    
    async def aset(self, data: str, value: Any, ttl: Optional[float] = None) -> None:
        """异步设置缓存"""
        key = self._compute_key(data)
        await self._cache.aset(key, value, ttl)


class SemanticCache:
    """语义缓存：基于嵌入向量的语义相似性缓存"""
    
    def __init__(
        self,
        max_size: int = 500,
        default_ttl: Optional[float] = 3600,
        similarity_threshold: float = 0.9,
    ):
        self._cache = LRUCache(max_size=max_size, default_ttl=default_ttl)
        self._embeddings: OrderedDict[str, list] = OrderedDict()
        self.similarity_threshold = similarity_threshold
        self._embedder = None
    
    def _get_embedder(self):
        """获取嵌入器（延迟加载）"""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                logger.warning("sentence-transformers not available, using simple text similarity")
                self._embedder = None
        return self._embedder
    
    def _compute_embedding(self, text: str) -> list:
        """计算文本嵌入"""
        embedder = self._get_embedder()
        if embedder is not None:
            return embedder.encode(text).tolist()
        
        return self._simple_text_hash(text)
    
    def _simple_text_hash(self, text: str) -> list:
        """简单文本哈希（备用方案）"""
        words = text.lower().split()
        return [hash(word) % 1000 for word in words[:100]]
    
    def _cosine_similarity(self, v1: list, v2: list) -> float:
        """计算余弦相似度"""
        if not v1 or not v2:
            return 0.0
        
        min_len = min(len(v1), len(v2))
        v1 = v1[:min_len]
        v2 = v2[:min_len]
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _compute_key(self, text: str) -> str:
        """计算缓存键"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def get(self, query: str) -> Optional[Any]:
        """获取语义相似的缓存"""
        query_embedding = self._compute_embedding(query)
        
        best_match = None
        best_similarity = 0.0
        
        for key, embedding in list(self._embeddings.items()):
            similarity = self._cosine_similarity(query_embedding, embedding)
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_match = key
        
        if best_match:
            self._embeddings.move_to_end(best_match)
            return self._cache.get(best_match)
        
        return None
    
    def set(self, query: str, value: Any, ttl: Optional[float] = None) -> None:
        """设置语义缓存"""
        key = self._compute_key(query)
        embedding = self._compute_embedding(query)
        
        self._cache.set(key, value, ttl)
        
        if key in self._embeddings:
            self._embeddings.move_to_end(key)
        else:
            if len(self._embeddings) >= self._cache.max_size:
                oldest_key, _ = self._embeddings.popitem(last=False)
            self._embeddings[key] = embedding
    
    def delete(self, query: str) -> bool:
        """删除缓存"""
        key = self._compute_key(query)
        if key in self._embeddings:
            del self._embeddings[key]
        return self._cache.delete(key)
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._embeddings.clear()
    
    def stats(self) -> dict:
        """获取统计信息"""
        stats = self._cache.stats()
        stats["semantic_entries"] = len(self._embeddings)
        return stats
    
    async def aget(self, query: str) -> Optional[Any]:
        """异步获取语义缓存"""
        return self.get(query)
    
    async def aset(self, query: str, value: Any, ttl: Optional[float] = None) -> None:
        """异步设置语义缓存"""
        self.set(query, value, ttl)


class HybridCache:
    """混合缓存：结合精确缓存和语义缓存"""
    
    def __init__(
        self,
        exact_max_size: int = 1000,
        exact_ttl: Optional[float] = 3600,
        semantic_max_size: int = 500,
        semantic_ttl: Optional[float] = 3600,
        similarity_threshold: float = 0.9,
    ):
        self.exact_cache = ExactCache(max_size=exact_max_size, default_ttl=exact_ttl)
        self.semantic_cache = SemanticCache(
            max_size=semantic_max_size,
            default_ttl=semantic_ttl,
            similarity_threshold=similarity_threshold,
        )
    
    def get(self, query: str) -> Optional[Any]:
        """获取缓存（先精确，后语义）"""
        result = self.exact_cache.get(query)
        if result is not None:
            return result
        
        return self.semantic_cache.get(query)
    
    def set(self, query: str, value: Any, ttl: Optional[float] = None) -> None:
        """设置缓存（同时设置精确和语义）"""
        self.exact_cache.set(query, value, ttl)
        self.semantic_cache.set(query, value, ttl)
    
    def delete(self, query: str) -> bool:
        """删除缓存"""
        exact_deleted = self.exact_cache.delete(query)
        semantic_deleted = self.semantic_cache.delete(query)
        return exact_deleted or semantic_deleted
    
    def clear(self) -> None:
        """清空所有缓存"""
        self.exact_cache.clear()
        self.semantic_cache.clear()
    
    def stats(self) -> dict:
        """获取统计信息"""
        return {
            "exact": self.exact_cache.stats(),
            "semantic": self.semantic_cache.stats(),
        }
    
    async def aget(self, query: str) -> Optional[Any]:
        """异步获取缓存"""
        result = await self.exact_cache.aget(query)
        if result is not None:
            return result
        return await self.semantic_cache.aget(query)
    
    async def aset(self, query: str, value: Any, ttl: Optional[float] = None) -> None:
        """异步设置缓存"""
        await self.exact_cache.aset(query, value, ttl)
        await self.semantic_cache.aset(query, value, ttl)
