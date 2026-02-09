from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional
from datetime import datetime


Action = Literal["BUY", "SELL", "HOLD"]
DecisionType = Literal["EXECUTE", "RESIZE", "HOLD", "BLOCK", "REVIEW"]
Mode = Literal["NORMAL", "LIMITED", "SAFE"]


class MarketSnapshot(BaseModel):
    price: float
    spread_pct: float = Field(ge=0)
    slippage_estimate_pct: float = Field(ge=0)
    latency_ms: int = Field(ge=0)
    data_age_seconds: float = Field(ge=0)


class DecisionIntent(BaseModel):
    action: Action
    asset: str = Field(min_length=1)
    size: float = Field(gt=0)  # fraction of equity (e.g., 0.05 = 5%)
    confidence: float = Field(ge=0, le=1)
    features_snapshot: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Position(BaseModel):
    asset: str
    size: float  # fraction of equity


class SystemState(BaseModel):
    equity: float = Field(gt=0)
    daily_pnl_pct: float = 0.0
    max_drawdown_pct: float = 0.0
    mode: Mode = "NORMAL"
    open_positions: List[Position] = Field(default_factory=list)

    # Safe-mode / recovery tracking
    safe_mode_latched_at: Optional[datetime] = None
    last_normal_seen_at: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None


class DecisionOutcome(BaseModel):
    decision: DecisionType
    approved_size: float = 0.0
    reason_codes: List[str] = Field(default_factory=list)
    mode: Mode
