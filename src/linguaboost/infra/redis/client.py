from redis.asyncio import Redis


def create_redis(url: str) -> Redis:
    return Redis.from_url(url, decode_responses=True)


async def claim_update(redis: Redis, update_id: int, ttl_seconds: int = 172_800) -> bool:
    key = f"dedup:telegram:update:{update_id}"
    return bool(await redis.set(key, "1", nx=True, ex=ttl_seconds))
