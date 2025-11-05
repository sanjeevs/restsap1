from fastapi import FastAPI

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

@app.get("/healthz")
def healthz():
    return {"status": "Hello World"}
