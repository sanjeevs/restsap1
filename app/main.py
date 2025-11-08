from fastapi import FastAPI, HTTPException, status
import os
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field
from typing import Dict
from threading import Lock
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()

DB_URL = os.getenv("DATABASE_URL", "").strip()
if not DB_URL:
    raise RuntimeError(
        "DATABASE_URL is required but not set. "
        " For local do export DATABASE_URL "
        " or start uvicorn with --env-file .env"
    )

engine = create_engine(DB_URL, pool_pre_ping=True, pool_recycle=1800)

v1 = APIRouter(prefix="/v1", tags=["v1"])

# CORS: who can call this API from a browser.
ALLOWED_ORIGINS = [
    "https://restsap1.snjv.us",      # your web app
    "http://localhost:3000",    # local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["*"],
)

BUILD_INFO = {
    "commit": os.getenv("RENDER_GIT_COMMIT", "unknown"),
    "branch": os.getenv("RENDER_GIT_BRANCH", "unknown"),
}

@app.get("/_meta")
def meta():
    return BUILD_INFO

@app.get("/healthz")
def healthz():
    return {"status": "Hello World"}

@app.get("/", include_in_schema=False)
def root():
    return JSONResponse({
        "service": os.getenv("SERVICE_NAME", "restsap1"),
        "now_utc": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "health": "/healthz",
            "meta": "/_meta",
        },
        "notes": "Prototype server OK. See /healthz and /_meta"
    })

@app.get("/_db", include_in_schema=False)
def db_health():
    if not engine:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not configured")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"db": "ok"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"db error: {type(e).__name__}")

@v1.get("/namaste")
def namaste():
    return {"status": "Namaste World"}

class ItemIn(BaseModel):
    name: str = Field(..., description="The name of the item", min_length=1, max_length=100)
    quantity: int = Field(..., ge=1, le=1_000_000)

class ItemOut(BaseModel):
    id: str
    name: str
    quantity: int
    created_at: str

_ITEMS: Dict[str, ItemOut] = {}
_ITEMS_LOCK = Lock()


# This is  a collection of items. Posting is adding one more item to the list.
@v1.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemIn):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    item_id = uuid.uuid4().hex[:12]
    item = ItemOut(id=item_id, name=payload.name, quantity=payload.quantity, created_at=now)
    with _ITEMS_LOCK:
        _ITEMS[item_id] = item
    # Here is the final version that the user created.
    return item

@v1.get("/items/{item_id}", response_model=ItemOut)
def get_items(item_id: str):
    with _ITEMS_LOCK:
        item = _ITEMS.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

app.include_router(v1)