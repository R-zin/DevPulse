from fastapi import APIRouter,HTTPException,Query
from ..services import docker_service
from ..models.schemas import *

router = APIRouter()

@router.get("/",response_model=list[ContainerSummary])
async def list_containers():
    pass