from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from models.database import access_logs, users, locations
from services.auth import require_admin_or_professor

router = APIRouter(prefix="/analytics", tags=["Analytics"])

PERIODS = {"24h": 86400, "7d": 604800, "30d": 2592000}


@router.get("")
def get_analytics(period: str = Query("7d"), current_user: dict = Depends(require_admin_or_professor)):
    seconds = PERIODS.get(period, PERIODS["7d"])
    since = datetime.utcnow() - timedelta(seconds=seconds)

    filtered = [l for l in access_logs if datetime.fromisoformat(l["timestamp"].replace("Z", "")) >= since]

    total      = len(filtered)
    permitidos = sum(1 for l in filtered if l["result"] == "permitido")
    negados    = total - permitidos
    taxa       = round((permitidos / total * 100), 1) if total else 0

    # Por local
    by_loc: dict = {}
    for l in filtered:
        lid = l["location_id"]
        if lid not in by_loc:
            by_loc[lid] = {"id": lid, "name": l["location_name"], "total": 0, "permitidos": 0, "negados": 0}
        by_loc[lid]["total"] += 1
        by_loc[lid]["permitidos" if l["result"] == "permitido" else "negados"] += 1

    # Por role
    by_role: dict = {}
    for l in filtered:
        r = l.get("user_role") or "desconhecido"
        if r not in by_role:
            by_role[r] = {"role": r, "total": 0}
        by_role[r]["total"] += 1

    # Por hora
    by_hour = [{"hour": h, "total": 0} for h in range(24)]
    for l in filtered:
        dt_utc = datetime.fromisoformat(l["timestamp"].replace("Z", ""))
        dt_local = dt_utc - timedelta(hours=3)
        by_hour[dt_local.hour]["total"] += 1

    # Por dia
    by_day: dict = {}
    for l in filtered:
        day = l["timestamp"][:10]
        if day not in by_day:
            by_day[day] = {"date": day, "total": 0, "permitidos": 0, "negados": 0}
        by_day[day]["total"] += 1
        by_day[day]["permitidos" if l["result"] == "permitido" else "negados"] += 1

    # Top usuários
    by_user: dict = {}
    for l in filtered:
        uid = l["user_id"]
        if uid not in by_user:
            by_user[uid] = {"userId": uid, "name": l["user_name"], "role": l.get("user_role"), "total": 0}
        by_user[uid]["total"] += 1

    return {
        "period": period,
        "kpis": {
            "total": total,
            "permitidos": permitidos,
            "negados": negados,
            "taxaAcesso": taxa,
            "totalUsuarios": sum(1 for u in users if u["active"]),
            "totalLocais": sum(1 for l in locations if l["active"]),
        },
        "byLocation": sorted(by_loc.values(), key=lambda x: -x["total"]),
        "byRole":     sorted(by_role.values(), key=lambda x: -x["total"]),
        "byHour":     by_hour,
        "byDay":      sorted(by_day.values(), key=lambda x: x["date"]),
        "topUsers":   sorted(by_user.values(), key=lambda x: -x["total"])[:10],
    }
