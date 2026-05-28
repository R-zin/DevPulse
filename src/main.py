from fastapi import HTTPException
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .services.redis_client import redis_Client
from .routers import alerts,containers,log,websocket
from .services.docker_service import docker_service
from .services.redis_client import redis_Client
@asynccontextmanager
async def lifespan(app:FastAPI):
    await redis_Client.connect()
    yield
    await redis_Client.disconnect()


app = FastAPI(title="Devpulse",lifespan=lifespan)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(containers.router,prefix="/containers")
app.include_router(alerts.router,prefix="/alert")
app.include_router(log.router,prefix="/logs")
app.include_router(websocket.router)

@app.get("/health")
async def health_check():
    return {"status":"OK"}
@app.get("/ready")
async def check_status():
    try:
        await docker_service.health_check()
        await redis_Client.check_health()
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))





