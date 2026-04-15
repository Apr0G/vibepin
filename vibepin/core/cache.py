import hashlib
from cachetools import TTLCache
from vibepin.core.config import settings

# In-memory cache — survives as long as the process is running.
# Swap the get/set calls for Redis if you need persistence across restarts.
_cache: TTLCache = TTLCache(maxsize=1000, ttl=settings.cache_ttl_seconds)


def image_key(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def url_key(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def get(key: str):
    return _cache.get(key)


def set(key: str, value) -> None:
    _cache[key] = value
