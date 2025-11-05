from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

# CORS: who can call this API from a browser.
ALLOWED_ORIGINS = [
    "https://app.snjv.us",      # your web app
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
    "build_time": os.getenv("RENDER_BUILD_TIME", "unknown"),
    "build_id": os.getenv("RENDER_BUILD_ID", "unknown"),
    "build_number": os.getenv("RENDER_BUILD_NUMBER", "unknown"),
    "build_url": os.getenv("RENDER_BUILD_URL", "unknown"),
    "build_status": os.getenv("RENDER_BUILD_STATUS", "unknown"),
    "build_status_url": os.getenv("RENDER_BUILD_STATUS_URL", "unknown"),
}

@app.get("/_meta")
def meta():
    return BUILD_INFO

@app.get("/healthz")
def healthz():
    return {"status": "Hello World"}
