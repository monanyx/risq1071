from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .models import SystemState

ROOT = Path(__file__).resolve().parents[2]  # project root (where config.json lives)
STATE_PATH = ROOT / "state.json"
CONFIG_PATH = ROOT / "config.json"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def load_config() -> Dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def default_state() -> SystemState:
    return SystemState(
        equity=100000.0,
        daily_pnl_pct=0.0,
        max_drawdown_pct=0.0,
        mode="NORMAL",
        open_positions=[],
        safe_mode_latched_at=None,
        last_normal_seen_at=_utcnow(),
        cooldown_until=None,
    )


def load_state() -> SystemState:
    if not STATE_PATH.exists():
        s = default_state()
        save_state(s)
        return s

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return SystemState.model_validate(raw)


def save_state(state: SystemState) -> None:
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state.model_dump(mode="json"), f, indent=2)


def set_mode(state: SystemState, mode: str) -> SystemState:
    state.mode = mode  # type: ignore
    if mode == "NORMAL":
        state.last_normal_seen_at = _utcnow()
    return state


def in_cooldown(state: SystemState) -> bool:
    if state.cooldown_until is None:
        return False
    return _utcnow() < state.cooldown_until
