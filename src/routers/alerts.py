from fastapi import APIRouter,HTTPException
from ..models.schemas import AlertThreshold,set_url
from ..services.redis_client import redis_Client
from ..services.alert_service import alert_service
router = APIRouter()

@router.get("/config",response_model=AlertThreshold)
async def get_alert_config():
    config = await redis_Client.get_alert_config()
    if not config:
        return AlertThreshold()
    return AlertThreshold(**config)

@router.put("/config")
async def update_alert_config(config:AlertThreshold):
    await redis_Client.set_alert_config(config.model_dump())
    return config

@router.delete("/config")
async def delete_alert_config():
    await redis_Client.delete("devpulse:alert_config")
    return {"message":"Successfully deleted"}

@router.post("/config_url")
def set_url(data:set_url):
    try:
        alert_service.url = data.slack_url
        return {"message":"Successfully updated slack link"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))



