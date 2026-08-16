"""Fact Store & Query Interface for The Senate State Engine."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from senate.state.db import Database
from senate.state.models import Fact, Hypothesis, ProjectState, Trial


class FactStore:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    # --- Facts CRUD ---
    def set_fact(self, fact: Fact) -> None:
        with self.db.get_connection() as conn:
            # Check if immutable and exists
            cur = conn.execute("SELECT is_immutable, value, source_artifact FROM facts WHERE key = ?", (fact.key,))
            existing = cur.fetchone()
            if existing and existing["is_immutable"]:
                raise ValueError(f"CRITICAL: Cannot overwrite immutable fact '{fact.key}'. It is permanently locked.")

            val_str = json.dumps(fact.value) if not isinstance(fact.value, (str, int, float, bool)) else fact.value
            
            # Record audit history if updating existing fact
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
            return Fact.from_row(tuple(row))

    def list_facts(self, domain: Optional[str] = None) -> List[Fact]:
        with self.db.get_connection() as conn:
            if domain:
                cur = conn.execute("SELECT key, domain, value, source_artifact, verified_at, verified_by, is_immutable FROM facts WHERE domain = ? ORDER BY key", (domain,))
            else:
                cur = conn.execute("SELECT key, domain, value, source_artifact, verified_at, verified_by, is_immutable FROM facts ORDER BY domain, key")
            return [Fact.from_row(tuple(r)) for r in cur.fetchall()]

    def delete_fact(self, key: str) -> bool:
        with self.db.get_connection() as conn:
            cur = conn.execute("DELETE FROM facts WHERE key = ? AND is_immutable = 0", (key,))
            conn.commit()
            return cur.rowcount > 0

    # --- Hypotheses CRUD ---
    def save_hypothesis(self, hypo: Hypothesis) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO hypotheses (hypo_id, domain, statement, status, kill_criterion, acceptance_bar, created_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(hypo_id) DO UPDATE SET
                    domain = excluded.domain,
                    statement = excluded.statement,
                    status = excluded.status,
                    kill_criterion = excluded.kill_criterion,
                    acceptance_bar = excluded.acceptance_bar,
                    notes = excluded.notes
                """,
                (
                    hypo.hypo_id,
                    hypo.domain,
                    hypo.statement,
                    hypo.status,
                    json.dumps(hypo.kill_criterion),
                    json.dumps(hypo.acceptance_bar),
                    hypo.created_at,
                    hypo.notes,
                ),
            )
            conn.commit()

    def get_hypothesis(self, hypo_id: str) -> Optional[Hypothesis]:
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT hypo_id, domain, statement, status, kill_criterion, acceptance_bar, created_at, notes FROM hypotheses WHERE hypo_id = ?", (hypo_id,))
            row = cur.fetchone()
            if not row:
                return None
            return Hypothesis(
                hypo_id=row["hypo_id"],
                domain=row["domain"],
                statement=row["statement"],
                status=row["status"],
                kill_criterion=json.loads(row["kill_criterion"]),
                acceptance_bar=json.loads(row["acceptance_bar"]),
                created_at=row["created_at"],
                notes=row["notes"] or "",
            )

    def list_hypotheses(self, domain: Optional[str] = None, status: Optional[str] = None) -> List[Hypothesis]:
        query = "SELECT hypo_id, domain, statement, status, kill_criterion, acceptance_bar, created_at, notes FROM hypotheses"
        params = []
        conds = []
        if domain:
            conds.append("domain = ?")
            params.append(domain)
        if status:
            conds.append("status = ?")
            params.append(status)
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY created_at DESC"

        with self.db.get_connection() as conn:
            cur = conn.execute(query, tuple(params))
            results = []
            for r in cur.fetchall():
                results.append(
                    Hypothesis(
                        hypo_id=r["hypo_id"],
                        domain=r["domain"],
                        statement=r["statement"],
                        status=r["status"],
                        kill_criterion=json.loads(r["kill_criterion"]),
                        acceptance_bar=json.loads(r["acceptance_bar"]),
                        created_at=r["created_at"],
                        notes=r["notes"] or "",
                    )
                )
            return results

    # --- Trials Ledger ---
    def log_trial(self, trial: Trial) -> int:
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO trials_ledger (project, config_hash, description, count, logged_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (trial.project, trial.config_hash, trial.description, trial.count, trial.logged_at),
            )
            conn.commit()
            return cur.lastrowid

    def get_trial_counts(self, project: Optional[str] = None) -> Tuple[Dict[str, int], int]:
        with self.db.get_connection() as conn:
            if project:
                cur = conn.execute("SELECT project, SUM(count) as total FROM trials_ledger WHERE project = ? GROUP BY project", (project,))
            else:
                cur = conn.execute("SELECT project, SUM(count) as total FROM trials_ledger GROUP BY project")
            per_project = {r["project"]: r["total"] for r in cur.fetchall()}
            cur_tot = conn.execute("SELECT SUM(count) as global_total FROM trials_ledger")
            row = cur_tot.fetchone()
            global_total = (row["global_total"] or 0) if row else 0
            return per_project, global_total

    # --- Project State ---
    def save_project_state(self, state: ProjectState) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO project_state (project_id, name, status, variables, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    name = excluded.name,
                    status = excluded.status,
                    variables = excluded.variables,
                    updated_at = excluded.updated_at
                """,
                (state.project_id, state.name, state.status, json.dumps(state.variables), state.updated_at),
            )
            conn.commit()

    def get_project_state(self, project_id: str) -> Optional[ProjectState]:
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT project_id, name, status, variables, updated_at FROM project_state WHERE project_id = ?", (project_id,))
            row = cur.fetchone()
            if not row:
                return None
            return ProjectState(
                project_id=row["project_id"],
                name=row["name"],
                status=row["status"],
                variables=json.loads(row["variables"]),
                updated_at=row["updated_at"],
            )

    def list_project_states(self) -> List[ProjectState]:
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT project_id, name, status, variables, updated_at FROM project_state ORDER BY project_id")
            return [
                ProjectState(
                    project_id=r["project_id"],
                    name=r["name"],
                    status=r["status"],
                    variables=json.loads(r["variables"]),
                    updated_at=r["updated_at"],
                )
                for r in cur.fetchall()
            ]

    def delete_project_state(self, project_id: str) -> bool:
        with self.db.get_connection() as conn:
            cur = conn.execute("DELETE FROM project_state WHERE project_id = ?", (project_id,))
            conn.commit()
            return cur.rowcount > 0


