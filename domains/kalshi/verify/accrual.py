"""Deterministic Time-Weighted Accrual Engine for Kalshi Domain Pod.

INVARIANT: NEVER COMPUTE YIELD RATES IN NATURAL LANGUAGE CHAT.
All realized daily rates per $100 must be computed from primary timestamps, exact seat-hours,
and time-weighted escrow collateral.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AccrualCalculation:
    ticker: str
    seat_hours: float
    total_escrow_usd: float
    realized_credit_usd: float
    hourly_rate_usd: float
    effective_daily_rate_usd: float
    effective_daily_per_100_usd: float


def compute_time_weighted_accrual(
    ticker: str,
    seat_hours: float,
    escrow_usd: float,
    realized_credit_usd: float,
) -> AccrualCalculation:
    """Compute exact time-weighted yield rates deterministically.
    
    Formula:
      hourly_rate = realized_credit_usd / max(seat_hours, 0.001)
      effective_daily_rate = hourly_rate * 24.0
      effective_daily_per_100 = (effective_daily_rate / max(escrow_usd, 0.01)) * 100.0
    """
    if seat_hours <= 0.0:
        raise ValueError(f"Seat hours must be positive, got {seat_hours}")
    if escrow_usd <= 0.0:
        raise ValueError(f"Escrow USD must be positive, got {escrow_usd}")

    hourly_rate = round(realized_credit_usd / seat_hours, 6)
    daily_rate = round(hourly_rate * 24.0, 4)
    daily_per_100 = round((daily_rate / escrow_usd) * 100.0, 4)

    return AccrualCalculation(
        ticker=ticker,
        seat_hours=round(seat_hours, 2),
        total_escrow_usd=round(escrow_usd, 2),
        realized_credit_usd=round(realized_credit_usd, 4),
        hourly_rate_usd=hourly_rate,
        effective_daily_rate_usd=daily_rate,
        effective_daily_per_100_usd=daily_per_100,
    )
