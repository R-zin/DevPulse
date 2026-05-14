from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .services.redis_client import redis_Client
from .routers import alerts,containers,log,websocket
@asynccontextmanager
async def lifespan(app:FastAPI):
    await redis_Client.connect()
    yield
    await redis_Client.disconnect()


app = FastAPI(title="Devpulse",lifespan=lifespan)
#app.add_middleware(CORSMiddleware,
                 #  allow_orgins = ["http://localhost:5173"],
                 #  allow_credentials = True,
                  # allow_methods = ["*"],
                 #  allow_headers = ["*"])
app.include_router(containers.router,prefix="/containers")
app.include_router(alerts.router,prefix="/alert")
app.include_router(log.router,prefix="/logs")
app.include_router(websocket.router,prefix="/soc")

@app.get("/health")
async def health_check():
    return {"status":"OK"}


