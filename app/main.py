from fastapi import FastAPI, Request, HTTPException, Query
from app.config import settings
from app.models import init_db, check_db, insert_message, fetch_messages
from app.security import verify_signature
from app.schemas import WebhookMessage
import json
from datetime import datetime
from app.models import get_stats
import time
import uuid
from app.logging_utils import setup_logging, log_event
from fastapi import HTTPException

app = FastAPI(title="Lyftr Backend Assignment")


@app.on_event("startup")
def startup_event():
    setup_logging(settings.LOG_LEVEL)
    init_db()

@app.post("/webhook")
async def webhook(request: Request):
    start_time = time.time()
    request_id = str(uuid.uuid4())

    raw_body = await request.body()
    signature = request.headers.get("X-Signature")

    # ❌ Invalid or missing signature
    if not signature or not verify_signature(raw_body, signature):
        latency_ms = int((time.time() - start_time) * 1000)

        log_event({
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": "ERROR",
            "request_id": request_id,
            "method": "POST",
            "path": "/webhook",
            "status": 401,
            "latency_ms": latency_ms,
            "result": "invalid_signature",
        })

        raise HTTPException(status_code=401, detail="invalid signature")

    payload = await request.json()
    message = WebhookMessage(**payload)

    result = insert_message(message)
    latency_ms = int((time.time() - start_time) * 1000)

    log_event({
        "ts": datetime.utcnow().isoformat() + "Z",
        "level": "INFO",
        "request_id": request_id,
        "method": "POST",
        "path": "/webhook",
        "status": 200,
        "latency_ms": latency_ms,
        "message_id": message.message_id,
        "dup": result == "duplicate",
        "result": result,
    })

    return {"status": "ok"}

@app.get("/messages")
def list_messages(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    from_: str | None = Query(None, alias="from"),
    since: str | None = None,
    q: str | None = None,
):
    data, total = fetch_messages(
        limit=limit,
        offset=offset,
        from_msisdn=from_,
        since=since,
        q=q,
    )

    return {
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/stats")
def stats():
    return get_stats()
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    latency_ms = int((time.time() - start_time) * 1000)

    log_data = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "level": "INFO",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "latency_ms": latency_ms,
    }

    log_event(log_data)

    return response

@app.get("/health/live")
def health_live():
    # App is running
    return {"status": "alive"}


@app.get("/health/ready")
def health_ready():
    # Check DB connectivity
    if not check_db():
        raise HTTPException(status_code=503, detail="database not ready")

    # Check webhook secret
    if not settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="webhook secret not set")

    return {"status": "ready"}
