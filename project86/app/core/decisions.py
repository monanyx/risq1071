from __future__ import annotations
from typing import List

from .models import DecisionIntent, DecisionOutcome, SystemState
from .gates import risk_gate
from .state import in_cooldown


def decide(intent: DecisionIntent, state: SystemState, cfg: dict) -> DecisionOutcome:
    reasons: List[str] = []

    # Cooldown check (if we’re cooling down after breach)
    if in_cooldown(state):
        reasons.append("COOLDOWN_ACTIVE")
        return DecisionOutcome(
            decision="BLOCK",
            approved_size=0.0,
            reason_codes=reasons,
            mode=state.mode,
        )

    # Uncertainty gate (simple V1)
    min_conf = float(cfg["uncertainty"]["min_confidence"])
    if intent.confidence < min_conf:
        reasons.append("LOW_CONFIDENCE")
        return DecisionOutcome(
            decision="HOLD",
            approved_size=0.0,
            reason_codes=reasons,
            mode=state.mode,
        )

    # Risk gate
    rg_decision, approved_size, rg_reasons = risk_gate(intent, state, cfg)
    reasons.extend(rg_reasons)

    if rg_decision == "BLOCK":
        return DecisionOutcome(
            decision="BLOCK",
            approved_size=0.0,
            reason_codes=reasons,
            mode=state.mode,
        )

    if rg_decision == "RESIZE":
        return DecisionOutcome(
            decision="RESIZE",
            approved_size=approved_size,
            reason_codes=reasons,
            mode=state.mode,
        )

    return DecisionOutcome(
        decision="EXECUTE",
        approved_size=approved_size,
        reason_codes=reasons,
        mode=state.mode,
    )
