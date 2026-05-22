from pydantic import BaseModel,Field
from typing import Optional
from enum import Enum

class ContainerStatus(str,Enum):
    running = "running"
    exited = "exited"
    paused = "paused"
    restarting = " restarting"
    dead = "dead"
class ContainerSummary(BaseModel):
    id:str
    short_id:str
    name:str
    image:str
    status:str
    state:str
    created:str
    ports:dict
    labels:dict
class CPUStats(BaseModel):
    percent:float
    system_cpu_usage:int
    online_cpu:int
class MemoryStats(BaseModel):
    usage_mb:float
    limit_mb:float
    percent:float
class NetworkStats(BaseModel):
    rx_bytes: int
    tx_bytes: int
    rx_packets: int
    tx_packets: int
class ContainerStats(BaseModel):
    container_id: str
    container_name: str
    cpu: CPUStats
    memory: MemoryStats
    network: NetworkStats
    timestamp: str
class AlertThreshold(BaseModel):
    cpu_percent: float = Field(default=80.0, ge=0, le=100)
    memory_percent: float = Field(default=85.0, ge=0, le=100)
    webhook_url: Optional[str] = None
    enabled: bool = True
class AlertEvent(BaseModel):
    container_id: str
    container_name: str
    metric: str           # "cpu" or "memory"
    value: float
    threshold: float
    timestamp: str
class LogQuery(BaseModel):
    tail: int = Field(default=100, ge=1, le=5000)
    since: Optional[str] = None     # e.g. "10m", "1h", or ISO timestamp
    timestamps: bool = False
class ActionResponse(BaseModel):
    success: bool
    container_id: str
    message: str
class set_url(BaseModel):
    slack_url:str
class renameIn(BaseModel):
    container_id:str
    new_name:str

