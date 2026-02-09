from __future__ import annotations
from fastapi import FastAPI

from app.core.models import DecisionIntent
from app.core.state import load_state, load_config
from app.core.decision import decide

app = FastAPI(title="Decision Engine", version="0.2.0")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/config")
def get_config():
    return load_config()


@app.get("/state")
def get_state():
    return load_state().model_dump()


@app.post("/decide")
def post_decide(intent: DecisionIntent):
    cfg = load_config()
    state = load_state()
    outcome = decide(intent, state, cfg)
    return outcome.model_dump()
