"""Standing Multi-Model Ideation Organ for The Senate.

Executes continuous dialectical edge-finding:
1. Claude proposes novel market hypotheses from tape fuel.
2. Gemini (via MultiModelAdversary) red-teams the mechanics and executes 2-round kill tests.
3. Survivors and Graveyard are persisted in SQLite `ideation_registry`.
"""

import json
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from senate.models.adversary import MultiModelAdversary
from senate.state.db import Database


@dataclass
class IdeationRecord:
    idea_id: str
    domain: str
    hypothesis: str
    proposed_by_model: str
    audited_by_adversary: str
    adversary_status: str
    kill_test_spec: Dict[str, Any]
    status: str


class StandingIdeator:
    def __init__(self, db: Optional[Database] = None, adversary: Optional[MultiModelAdversary] = None):
        self.db = db or Database()
        self.adversary = adversary or MultiModelAdversary()

    def submit_and_audit_idea(
        self,
        domain: str,
        hypothesis: str,
        kill_test_spec: Dict[str, Any],
        proposing_model: str = "claude-3-7-sonnet",
        invariants: Optional[List[str]] = None,
    ) -> IdeationRecord:
        """Process a newly generated hypothesis through the 2-model adversarial audit gate."""
        inv_list = invariants or [
            "Must have decisive kill test with measurable dollar cost",
            "Must not violate empirical fundamental base rates",
            "Must survive 24h terminal book evacuation curfew",
        ]

        audit_res = self.adversary.audit_proposal(
            proposal_description=f"HYPOTHESIS: {hypothesis}\nKILL TEST: {json.dumps(kill_test_spec)}",
            invariants_list=inv_list,
            drafted_by_model=proposing_model,
        )

        idea_id = f"idea_{uuid.uuid4().hex[:8]}"
        adv_status = "SURVIVED" if audit_res.is_approved else "KILLED"
        final_status = "VALIDATED" if audit_res.is_approved else "GRAVEYARD"

        record = IdeationRecord(
            idea_id=idea_id,
            domain=domain,
            hypothesis=hypothesis,
            proposed_by_model=proposing_model,
            audited_by_adversary=audit_res.auditor_model,
            adversary_status=adv_status,
            kill_test_spec=kill_test_spec,
            status=final_status,
        )

        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO ideation_registry
                   (idea_id, domain, hypothesis, proposed_by_model, audited_by_adversary, adversary_status, kill_test_spec, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    record.idea_id,
                    record.domain,
                    record.hypothesis,
                    record.proposed_by_model,
                    record.audited_by_adversary,
                    record.adversary_status,
                    json.dumps(record.kill_test_spec),
                    record.status,
                ),
            )
            conn.commit()

        return record

    def list_ideas(self, domain: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List registered ideas and graveyard entries from SQLite."""
        query = "SELECT * FROM ideation_registry WHERE 1=1"
        params = []
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC"

        with self.db.get_connection() as conn:
            cur = conn.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

