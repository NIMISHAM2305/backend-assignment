from fastapi import FastAPI, Request, HTTPException, Query
from app.config import settings
from app.models import init_db, check_db, insert_message, fetch_messages
from app.security import verify_signature
from app.schemas import WebhookMessage
import json
from app.models import get_stats

app = FastAPI(title="Lyftr Backend Assignment")


@app.on_event("startup")
def startup_event():
    init_db()


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
