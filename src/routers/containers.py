import docker.errors
from fastapi import APIRouter,HTTPException,Query
from ..services.docker_service import docker_service
from ..models.schemas import ContainerStats,ContainerSummary,ActionResponse,renameIn
from ..services.redis_client import redis_Client
import json


router = APIRouter()

@router.get("/",response_model=list[ContainerSummary])
async def list_containers(all:bool = Query(default=True)): #Include Stopped container (all)
    try:
        return docker_service.list_all_containers()
    except Exception as e:
        raise HTTPException(status_code=500,detail="Error while fetching")

@router.get("/{container_id}/stats",response_model=ContainerStats)
async def get_container_stats(container_id:str):
    cached = await redis_Client.get_cached_stats(container_id)
    if cached:
        return ContainerStats(**json.loads(cached))
    try:
        stats = docker_service.get_stats(container_id)
    except docker.errors.NotFound:
        raise HTTPException(status_code=404,detail="Container Not Found")
    await redis_Client.cache_stats(container_id,stats.model_dump_json())

    return stats

@router.post("/{container_id}/start",response_model=ActionResponse)
async def start_container(container_id:str):
    try:
        docker_service.start_container(container_id)
        return ActionResponse(container_id=container_id,
                              success=True,
                              message="Container turned on successfully")
    except Exception as e:
        raise HTTPException(status_code=500,detail={e})

@router.post("/{container_id}/stop",response_model=ActionResponse)
async def stop_container(container_id:str,timeout:int = Query(default=10,ge=0)):
    try:
        docker_service.stop_container(container_id,timeout)
        return ActionResponse(container_id=container_id,
                              success=True,
                              message="Container Stopped")
    except Exception as e:
        raise HTTPException(status_code=500,detail={e})

@router.post("/{container_id}/restart",response_model=ActionResponse)
async def restart_container(container_id):
    try:
        docker_service.restart_container(container_id)
        return ActionResponse(container_id=container_id,
                              success=True,
                              message="Container restarted Successfully")
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@router.get("/{container_id}/tester_getinstant")
async def tester(container_id:str):
    try:
        res = docker_service.get_raw_data(container_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
@router.get("/{container_id}/generate_report")
async def generate_log_report(container_id:str):
    pass

@router.post("/rename")
async def rename(data:renameIn):
    try:
        docker_service.change_container_name(data.container_id,data.new_name)
        return {"Message":f"Container renamed successfully to {data.new_name}"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))





