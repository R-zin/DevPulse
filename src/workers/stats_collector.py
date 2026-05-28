import os
import asyncio
from ..services.docker_service import docker_service
from ..services.redis_client import redis_Client
QUEUE_NAME = os.getenv("REDIS_QUEUE_NAME")
async def collect_stats():
    while True:
        containers = docker_service.list_all_containers(False)
        for c in containers:
            stats = docker_service.get_stats(c.id)
            await redis_Client.enqueue(QUEUE_NAME,stats)
        await asyncio.sleep(5)

