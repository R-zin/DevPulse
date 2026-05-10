from fastapi import APIRouter,HTTPException,Query
from fastapi.responses import StreamingResponse
from ..services.docker_service import docker_service
import docker.errors
import docker

router = APIRouter()

@router.get("/{container_id}/logs",response_model=list[str])
async def get_logs(container_id:str,tail:int=Query(default=100,ge=1,le=500),since:str = Query(default=None),timestamp:bool = Query(default=False)):
    try:
        lines = docker_service.get_logs(container_id, tail=tail, since=since,timestamp=timestamp)
        return lines
    except docker.errors.NotFound:
        raise HTTPException(status_code=404,detail="Container not found")
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@router.get("/{container_id}/logs/stream")
async def stream_logs(container_id:str,tail: int = Query(default=50, ge=1, le=500),timestamps: bool = Query(default=False)):
    try:
        container = docker_service.client.containers.get(container_id)
    except docker.errors.NotFound:
        raise HTTPException(status_code=400,detail="Container not found")
    def event_stream():
        log_stream = container.logs(
            stdout=True,
            stderr=True,
            stream=True,
            follow=True,
            tail=tail,
            timestamps=timestamps,
        )
        for chunk in log_stream:
            line = chunk.decode("utf-8", errors="replace").rstrip()
            if line:
                yield f"data: {line}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering for SSE
        },
    )


