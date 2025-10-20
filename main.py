from fastapi import FastAPI, Request, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from bson import ObjectId
from datetime import datetime
from typing import Optional
from database import db
from models import LogCreate

app = FastAPI(title="FastAPI Log Server with Admin Panel")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/logs")
async def create_log(log: LogCreate):
    """Add new log entry (API endpoint)"""
    data = log.dict()
    data["timestamp"] = datetime.utcnow()
    result = await db.logs.insert_one(data)
    return {"status": "ok", "inserted_id": str(result.inserted_id)}


@app.get("/logs")
async def get_logs(limit: int = 50):
    """Fetch recent logs (API endpoint)"""
    cursor = db.logs.find().sort("timestamp", -1).limit(limit)
    logs = []
    async for log in cursor:
        log["_id"] = str(log["_id"])
        logs.append(log)
    return {"count": len(logs), "logs": logs}


# ----------------------------- ADMIN PANEL ----------------------------- #

@app.get("/", response_class=HTMLResponse)
async def admin_panel(
    request: Request,
    level: Optional[str] = Query(None),
    service: Optional[str] = Query(None)
):
    """Admin panel with filters by log level and service name"""
    query = {}
    if level:
        query["level"] = level.upper()
    if service:
        query["service"] = {"$regex": service, "$options": "i"}

    cursor = db.logs.find(query).sort("timestamp", -1).limit(100)
    logs = []
    async for log in cursor:
        log["_id"] = str(log["_id"])
        log["timestamp"] = log["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        logs.append(log)

    # Get distinct service names for dropdown filter
    services = await db.logs.distinct("service")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "logs": logs,
            "selected_level": level,
            "selected_service": service,
            "services": services,
        },
    )


@app.get("/log/{log_id}", response_class=HTMLResponse)
async def log_detail(request: Request, log_id: str):
    """View log details"""
    log = await db.logs.find_one({"_id": ObjectId(log_id)})
    if not log:
        return HTMLResponse("<h3>Log not found</h3>", status_code=404)

    log["_id"] = str(log["_id"])
    log["timestamp"] = log["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
    return templates.TemplateResponse("detail.html", {"request": request, "log": log})
