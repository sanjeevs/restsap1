from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

app = FastAPI()

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

@app.get("/healthz")
def healthz():
    return {"status": "Hello World"}

@app.get("/_meta")
def meta():
    return BUILD_INFO

@v1.get("/namaste")
def namaste():
    return {"status": "Namaste World"}

app.include_router(v1)