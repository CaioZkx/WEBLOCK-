from fastapi import APIRouter, HTTPException, Depends, Query
from models.database import access_logs
from services.auth import get_current_user

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("")
def list_logs(
    user_id: str = Query(None),
    location_id: str = Query(None),
    result: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    logs = list(access_logs)
    if user_id:     logs = [l for l in logs if l["user_id"] == user_id]
    if location_id: logs = [l for l in logs if l["location_id"] == location_id]
    if result:      logs = [l for l in logs if l["result"] == result]
    if start_date:  logs = [l for l in logs if l["timestamp"] >= start_date]
    if end_date:    logs = [l for l in logs if l["timestamp"] <= end_date]

    total = len(logs)
    start = (page - 1) * limit
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "logs": logs[start:start + limit],
    }


@router.get("/{log_id}")
def get_log(log_id: str, current_user: dict = Depends(get_current_user)):
    log = next((l for l in access_logs if l["id"] == log_id), None)
    if not log:
        raise HTTPException(status_code=404, detail="Log não encontrado.")
    return log
