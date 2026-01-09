from django.core.cache import cache
import time, json

def cache_get_or_set(key: str, builder_func, ttl_seconds: int):
    """Tenta pegar do cache; se não existir, chama builder_func(), guarda e retorna."""
    data = cache.get(key)
    if data is not None:
        return data, True  # True => veio do cache
    data = builder_func()
    # Evita cachear erros óbvios
    if isinstance(data, dict) and data.get("error"):
        return data, False
    cache.set(key, data, ttl_seconds)
    return data, False
