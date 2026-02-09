from __future__ import annotations
from typing import List, Tuple

from .models import DecisionIntent, DecisionOutcome, SystemState


def _gross_exposure(state: SystemState) -> float:
    # Sum of absolute open position sizes (fractions of equity)
    return sum(abs(p.size) for p in state.open_positions)


def risk_gate(
    intent: DecisionIntent,
    state: SystemState,
    cfg: dict,
) -> Tuple[str, float, List[str]]:
    """
    Returns: (decision, approved_size, reason_codes)
    decision in {"EXECUTE","RESIZE","BLOCK"}
    """
    reasons: List[str] = []
    approved_size = intent.size

    risk = cfg["risk"]

    max_single = float(risk["max_single_position"])
    max_gross = float(risk["max_gross_exposure"])
    max_trades_per_hour = int(risk["max_trades_per_hour"])
    daily_loss_limit = float(risk["daily_loss_limit_pct"])
    max_dd_limit = float(risk["max_drawdown_limit_pct"])

    # 1) Single position cap
    if approved_size > max_single:
        reasons.append("MAX_SINGLE_POSITION_EXCEEDED")
        approved_size = max_single

    # 2) Gross exposure cap
    current_gross = _gross_exposure(state)
    if current_gross + approved_size > max_gross:
        reasons.append("MAX_GROSS_EXPOSURE_EXCEEDED")
        # Resize to remaining capacity (or block if none)
        remaining = max_gross - current_gross
        approved_size = max(0.0, remaining)

    # 3) Daily loss limit (if breached, block)
    # daily_pnl_pct is negative on loss; compare against -daily_loss_limit
    if state.daily_pnl_pct <= -daily_loss_limit:
        reasons.append("DAILY_LOSS_LIMIT_BREACHED")
        return "BLOCK", 0.0, reasons

    # 4) Max drawdown limit (if breached, block)
    if state.max_drawdown_pct <= -max_dd_limit:
        reasons.append("MAX_DRAWDOWN_LIMIT_BREACHED")
        return "BLOCK", 0.0, reasons

    # (We’ll add trade-frequency tracking in the next step when logging exists)
    # For now we keep the config value but don’t enforce it yet.

    if approved_size <= 0:
        reasons.append("NO_RISK_CAPACITY")
        return "BLOCK", 0.0, reasons

    if approved_size < intent.size:
        return "RESIZE", appr
