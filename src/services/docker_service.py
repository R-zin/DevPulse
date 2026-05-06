import docker
import json
from datetime import datetime,timezone
from typing import Optional
from ..models.schemas import (ContainerStats,ContainerSummary,CPUStats,MemoryStats,NetworkStats)

class DockerService:
    def __init__(self):
        self.client = docker.from_env()
    def parse_cpu_percent(self,stats:dict):
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"]-stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"].get("system_cpu_usage",0) - stats["precpu_stats"].get("system_cpu_usage",0)
        online_cpus = stats["cpu_stats"].get("online_cpu",len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage",[1])))
        percent = 0.0
        if system_delta > 0:
            percent = (cpu_delta/system_delta)*online_cpus*100.0
        return CPUStats(percent=round(percent,2),system_cpu_usage=stats["cpu_stats"].get("system_cpu_usage",0),online_cpu=online_cpus)
    def parse_memory(self,stats:dict):
        mem = stats["memory_stats"]
        usage = mem.get("usage",0)
        cache = mem["usage"]["cache"]
        real_usage = usage - cache
        limit = mem.get("limit",1)
        return MemoryStats(usage_mb=round((real_usage/(1024**2)),2),
                           limit_mb=round((limit/(1024**2)),2),
                           percent=round(((real_usage/limit)*100),2))
    def parse_network(self,stats:dict):
        network = stats["network"]
        rx_bytes = tx_bytes = rx_packets = tx_packets = 0
        for i in network.values():
            rx_bytes += i.get("rx_bytes",0)
            tx_bytes += i.get("tx_bytes",0)
            rx_packets += i.get("rx_packets",0)
            tx_packets += i.get("tx_packets",0)
        return NetworkStats(
            rx_bytes=rx_bytes,
            tx_bytes=tx_bytes,
            rx_packets=rx_packets,
            tx_packets=tx_packets,
        )
    def list_all_containers(self):
        containers = self.client.containers.list(all=True)
        result = []
        for c in containers:
            ports = {}
            for port, bindings in (c.ports or {}).items():
                ports[port] = bindings[0]["Hostport"] if bindings else None
            result.append(
                ContainerSummary(
                    id=c.id,
                    short_id=c.short_id,
                    name=c.name,
                    image= c.image.tags[0] if c.image.tags else c.short_id,
                    status=c.status,
                    state=c.attrs["State"]["Status"],
                    created = c.attrs["Created"],
                    ports=ports,
                    labels=c.labels or {}
                )
            )
        return result

