from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from models.orm_models import AccessLog, User
from database_config import get_db
from services.auth import get_current_user

router = APIRouter(prefix="/logs", tags=["Logs"])


def _serialize(log: AccessLog) -> dict:
    return {
        "id": log.id, "user_id": log.user_id, "user_name": log.user_name, "user_role": log.user_role,
        "location_id": log.location_id, "location_name": log.location_name,
        "result": log.result, "reason": log.reason,
        "timestamp": log.timestamp.isoformat() + "Z" if log.timestamp else None,
        "device_ip": log.device_ip,
    }


@router.get("")
def list_logs(
    user_id: str = Query(None),
    location_id: str = Query(None),
    result: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AccessLog)
    if user_id:     query = query.filter(AccessLog.user_id == user_id)
    if location_id: query = query.filter(AccessLog.location_id == location_id)
    if result:      query = query.filter(AccessLog.result == result)
    if start_date:  query = query.filter(AccessLog.timestamp >= start_date)
    if end_date:    query = query.filter(AccessLog.timestamp <= end_date)

    query = query.order_by(AccessLog.timestamp.desc())
    total = query.count()
    start = (page - 1) * limit
    logs = query.offset(start).limit(limit).all()

    return {
        "total": total, "page": page, "limit": limit,
        "pages": (total + limit - 1) // limit,
        "logs": [_serialize(l) for l in logs],
    }


@router.get("/{log_id}")
def get_log(log_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = db.query(AccessLog).filter(AccessLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log não encontrado.")
    return _serialize(log)
