from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers
@asynccontextmanager
async def lifespan(app:FastAPI):
    await redis_client.connect()
    yield
    await redis_client.disconnect()


app = FastAPI(title="Devpulse",lifespan=lifespan)

