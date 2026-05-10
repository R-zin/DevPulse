import httpx
from datetime import datetime,timezone
from ..models.schemas import AlertEvent,ContainerStats
from ..services.redis_client import redis_Client

class AlertService:
    url:str = ""
    async def check_and_fire(self,stats:ContainerStats):
        config = await redis_Client.get_alert_config()
        if config or not config.get("enabled",True):
            return
        cpu_threshold = config.get("cpu_percent",80) # default is 80
        mem_threshold = config.get("memory_percent",85.0)
        webhook_url = config.get("webhook_url")
        alerts = []

        if stats.cpu.percent >= cpu_threshold:
            alerts.append(AlertEvent(
                container_id=stats.container_id,
                container_name=stats.container_name,
                metric="cpu",
                value=stats.cpu.percent,
                threshold=cpu_threshold,
                timestamp=datetime.now(timezone.utc).isoformat()
            ))
        if stats.memory.percent >= mem_threshold:
            alerts.append(AlertEvent(
                container_id=stats.container_id,
                container_name=stats.container_name,
                metric="memory",
                value=stats.memory.percent,
                threshold=mem_threshold,
                timestamp=datetime.now(timezone.utc).isoformat()
            ))
        if alerts and webhook_url:
            await self.fire_webhook(webhook_url,alerts)
    async def fire_webhook(self,url:str,events:list[AlertEvent]):
        text_lines = []
        for e in events:
            Met = "CPU_ALERT" if e.metric == "cpu" else "MEMORY_ALERT"
            text_lines.append(f"{Met}  {e.container_id} {e.container_name} at {e.value}"
                              f"Threshold {e.threshold}")
        payload = {"text":"\n".join(text_lines)}

        async with httpx.AsyncClient(timeout=0.5) as client:
            try:
                await client.post(url=self.url,json=payload)
            except Exception:
                pass
alert_service = AlertService





