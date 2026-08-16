"""Fact and Seat Store for Kalshi Domain Pod."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from domains.kalshi.state.db import Database
from domains.kalshi.state.models import ActiveOrder, Fact


class FactStore:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    # --- Facts CRUD ---
    def set_fact(self, fact: Fact) -> None:
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT is_immutable, value, source_artifact FROM facts WHERE key = ?", (fact.key,))
            existing = cur.fetchone()
            if existing and existing["is_immutable"]:
                raise ValueError(f"CRITICAL: Cannot overwrite immutable fact '{fact.key}'. It is permanently locked.")

            val_str = json.dumps(fact.value) if not isinstance(fact.value, (str, int, float, bool)) else fact.value
            
            if existing:
                conn.execute(
                    """
                    INSERT INTO fact_history (key, old_value, new_value, changed_by, source_artifact)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (fact.key, existing["value"], val_str if isinstance(val_str, str) else json.dumps(val_str), fact.verified_by, fact.source_artifact),
                )

            conn.execute(
                """
                INSERT INTO facts (key, domain, value, source_artifact, verified_at, verified_by, is_immutable)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    domain = excluded.domain,
                    value = excluded.value,
                    source_artifact = excluded.source_artifact,
                    verified_at = excluded.verified_at,
                    verified_by = excluded.verified_by,
                    is_immutable = excluded.is_immutable
                """,
                (
                    fact.key,
                    fact.domain,
                    val_str if isinstance(val_str, str) else json.dumps(val_str),
                    fact.source_artifact,
                    fact.verified_at,
                    fact.verified_by,
                    1 if fact.is_immutable else 0,
                ),
            )
            conn.commit()

    def get_fact(self, key: str) -> Optional[Fact]:
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT key, domain, value, source_artifact, verified_at, verified_by, is_immutable FROM facts WHERE key = ?", (key,))
            row = cur.fetchone()
            if not row:
                return None
            val = json.loads(row["value"]) if isinstance(row["value"], str) else row["value"]
            return Fact(
                key=row["key"],
                domain=row["domain"],
                value=val,
                source_artifact=row["source_artifact"],
                verified_at=row["verified_at"],
                verified_by=row["verified_by"],
                is_immutable=bool(row["is_immutable"]),
            )

    def list_facts(self) -> List[Fact]:
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT key, domain, value, source_artifact, verified_at, verified_by, is_immutable FROM facts ORDER BY key ASC")
            results = []
            for row in cur.fetchall():
                val = json.loads(row["value"]) if isinstance(row["value"], str) else row["value"]
                results.append(Fact(
                    key=row["key"],
                    domain=row["domain"],
                    value=val,
                    source_artifact=row["source_artifact"],
                    verified_at=row["verified_at"],
                    verified_by=row["verified_by"],
                    is_immutable=bool(row["is_immutable"]),
                ))
            return results

    # --- Active Orders ---
    def save_order(self, order: ActiveOrder) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO active_orders (order_id, ticker, side, price, count, collateral_usd, status, lane, placed_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(order_id) DO UPDATE SET
                    ticker = excluded.ticker,
                    side = excluded.side,
                    price = excluded.price,
                    count = excluded.count,
                    collateral_usd = excluded.collateral_usd,
                    status = excluded.status,
                    lane = excluded.lane,
                    updated_at = excluded.updated_at
                """,
                (
                    order.order_id,
                    order.ticker,
                    order.side,
                    order.price,
                    order.count,
                    order.collateral_usd,
                    order.status,
                    order.lane,
                    order.placed_at,
                    order.updated_at,
                ),
            )
            conn.commit()

    def list_active_orders(self) -> List[ActiveOrder]:
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT order_id, ticker, side, price, count, collateral_usd, status, lane, placed_at, updated_at FROM active_orders WHERE status = 'RESTING'")
            return [ActiveOrder(**dict(row)) for row in cur.fetchall()]

