import asyncio
import json
from fastapi import APIRouter,WebSocket,HTTPException,WebSocketDisconnect,Query
from src.services.alert_service import alert_service
from src.services.docker_service import docker_service
from src.services.redis_client import redis_Client
from src.Setting import POLL_INTERVAL

router = APIRouter()
@router.websocket("/ws/stats/{container_id}")
async def container_stats(websocket: WebSocket,container_id: str):
    await websocket.accept()
    try:
        while True:
            stats = docker_service.get_stats(container_id)
            await websocket.send_text(
                json.dumps(
                    stats.model_dump(),
                    default=str
                )
            )
            await asyncio.sleep(POLL_INTERVAL)
    except WebSocketDisconnect:
        pass



@router.websocket("/ws/stats")
async def all_stats(websocket:WebSocket):
    await websocket.accept()
    try:
        while True:
            containers = docker_service.list_all_containers(False)
            payload = {"containers" : [], "timestamp":None}
            for c in containers:
                try:
                    stats = docker_service.get_stats(c.id)
                    await alert_service.check_and_fire(stats)
                    await redis_Client.cache_stats(c.short_id, stats.model_dump())
                    data = stats.model_dump()
                    payload["containers"].append(data)
                    payload["timestamp"] = data["timestamp"]
                except Exception:
                    continue
            await websocket.send_text(json.dumps(payload,default=str))
            await asyncio.sleep(POLL_INTERVAL)
    except WebSocketDisconnect:
        pass







