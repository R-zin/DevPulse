import datetime
from sqlmodel import SQLModel, Field


class ContainerMetrics(SQLModel,table=True):
    id: int  = Field(default=None,primary_key=True)
    container_id:str
    container_name:str

    cpu_percentage:float
    memory_usage:float
    net_rx:int
    net_tx:int
    timestamp:datetime = Field(index=True)

