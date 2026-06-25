import os
import json
import logging

import redis

logger = logging.getLogger("shop")

_redis_client: redis.Redis = None

REDIS_URL = os.getenv("REDIS_URL", "redis://:redis123@localhost:6379/0")


def init_redis():
    global _redis_client
    _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    _redis_client.ping()
    logger.info("Redis 客户端初始化完成")


def close_redis():
    global _redis_client
    if _redis_client:
        _redis_client.close()
        logger.info("Redis 客户端已关闭")


def get_cache(key: str):
    try:
        value = _redis_client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except Exception:
        logger.warning("Redis 读取失败 | key=%s", key, exc_info=True)
        return None


def set_cache(key: str, value, ttl: int = 600):
    try:
        _redis_client.setex(key, ttl, json.dumps(value, ensure_ascii=False, default=str))
    except Exception:
        logger.warning("Redis 写入失败 | key=%s", key, exc_info=True)


def delete_cache(key: str):
    try:
        _redis_client.delete(key)
    except Exception:
        logger.warning("Redis 删除失败 | key=%s", key, exc_info=True)


def delete_keys(*keys: str):
    if not keys:
        return
    try:
        pipe = _redis_client.pipeline()
        for key in keys:
            pipe.delete(key)
        pipe.execute()
    except Exception:
        logger.warning("Redis 批量删除失败 | keys=%s", keys, exc_info=True)