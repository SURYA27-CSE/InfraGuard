from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from agent import get_system_metrics
import os

app = FastAPI(title="InfraGuard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    frontend_path = os.path.join(
        os.path.dirname(__file__),
        "frontend",
        "index.html"
    )

    return FileResponse(frontend_path)


@app.get("/metrics")
def metrics():
    return get_system_metrics()