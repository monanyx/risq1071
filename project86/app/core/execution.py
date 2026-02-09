from __future__ import annotations
from typing import List, Tuple

from .models import DecisionIntent


def execution_gate(intent: DecisionIntent, cfg: dict) -> Tuple[str, List[str]]:
    """
    Returns: ("PASS" | "HOLD" | "BLOCK", reason_codes)
    """
    reasons: List[str] = []
    ex = cfg["execution"]

    # If no market snapshot provided, we play it safe
    if intent.market is None:
        reasons.append("NO_MARKET_SNAPSHOT")
        return "HOLD", reasons

    m = intent.market

    if m.spread_pct > float(ex["max_spread_pct"]):
        reasons.append("SPREAD_TOO_WIDE")
        return "HOLD", reasons

    if m.slippage_estimate_pct > float(ex["max_slippage_pct"]):
        reasons.append("SLIPPAGE_TOO_HIGH")
        return "HOLD", reasons

    if m.latency_ms > int(ex["max_latency_ms"]):
        reasons.append("LATENCY_TOO_HIGH")
        return "HOLD", reasons

    if m.data_age_seconds > float(ex["stale_data_seconds"]):
        reasons.append("STALE_DATA")
        return "BLOCK", reasons

    return "PASS", reasons
