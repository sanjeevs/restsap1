from fastapi import FastAPI

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "Hello World"}
