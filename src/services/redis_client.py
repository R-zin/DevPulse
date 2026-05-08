import json
import redis.asyncio as aioredis
from typing import Optional
from .. import Setting

class RedisClient:
    def __init__(self):
        self._client : Optional[aioredis.Redis] = None

    async def connect(self):
        self._client = aioredis.from_url(Setting.REDIS_URL,
                                        encoding='utf-8',
                                        decode_responses=True)
    async def disconnect(self):
        if self._client:
            await self._client.aclose()
    @property
    def client(self):
        if not self._client():
            raise RuntimeError("Redis not connected")
        return self._client()

    async def set_json(self,key:str,value:dict,ttl:int = 10):
        await self.client.set(key,json.dumps(value),ex=ttl)
    async def get_json(self,key:str):
        raw = await self.client.get(key)
        return json.loads(raw) if raw else None
    async def delete(self,key):
        await self.client.delete(key)
    async def publish(self,channel:str,message:dict):
        await self.client.publish(channel,json.dumps(message))

    async def get_alert_config(self) -> Optional[dict]:
        return await self.get_json("devpulse:alert_config")

    async def set_alert_config(self, config: dict):
        await self.client.set("devpulse:alert_config", json.dumps(config))

    async def cache_stats(self, container_id: str, stats: dict):
        key = f"devpulse:stats:{container_id}"
        await self.set_json(key, stats, ttl=10)

    async def get_cached_stats(self, container_id: str) -> Optional[dict]:
        return await self.get_json(f"devpulse:stats:{container_id}")

redis_Client = RedisClient()




