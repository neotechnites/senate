"""Cross-Model Adversarial Audit Engine for The Senate.

Breaks single-model echo chambers by using independent model providers (e.g. Gemini, OpenAI)
to red-team and audit proposals before execution or deployment.
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from senate.models.gateway import ModelGateway, ModelProvider, ModelResponse


@dataclass
class AdversarialAuditResult:
    is_approved: bool
    risk_score: int  # 1 (low) to 10 (critical)
    auditor_model: str
    auditor_provider: str
    violations: List[str]
    critique: str
    raw_response: str


class MultiModelAdversary:
    """Orchestrates independent adversarial audits across different model families."""

    def __init__(self, gateway: Optional[ModelGateway] = None):
        self.gateway = gateway or ModelGateway()

    def audit_proposal(
        self,
        proposal_description: str,
        invariants_list: List[str],
        drafted_by_model: str = "claude-3-5-sonnet",
        auditor_provider: Optional[ModelProvider] = None,
        auditor_model: Optional[str] = None,
    ) -> AdversarialAuditResult:
        """Submit a proposal to an independent model family for adversarial critique."""
        system_prompt = """You are an independent, adversarial red-team auditor.
Your job is NOT to be helpful, agreeable, or polite.
Your sole mandate is to locate:
1. False assumptions or hallucinated beliefs.
2. Invariant violations against stated domain laws.
3. Fail-open edge cases or unhandled failure states.
4. Economic, mathematical, or physical contradictions.

You must respond in strict JSON format:
{
  "is_approved": false,
  "risk_score": 8,
  "violations": ["Specific invariant breach 1", "Specific assumption flaw 2"],
  "critique": "Brutally honest 2-3 sentence explanation of the failure mode."
}"""

        invariants_text = "\n".join(f"- {inv}" for inv in invariants_list)
        user_prompt = f"""AUDIT TARGET (Drafted by {drafted_by_model}):
{proposal_description}

ENFORCED INVARIANTS & CONSTRAINTS:
{invariants_text}

Analyze the proposal rigorously against the invariants. If there is ANY loophole, unverified belief, or fail-open risk, set is_approved: false."""

        resp = self.gateway.query(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=auditor_provider,
            model=auditor_model,
            json_mode=True,
        )

        if resp.is_error:
            # If the auditor call fails, fail closed!
            return AdversarialAuditResult(
                is_approved=False,
                risk_score=10,
                auditor_model=resp.model_name,
                auditor_provider=resp.provider,
                violations=["Auditor unavailable or query failed (Fails closed)"],
                critique=f"Adversarial review failed: {resp.error_message}",
                raw_response="",
            )

        try:
            # Parse JSON response
            cleaned = resp.content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            parsed = json.loads(cleaned)

            return AdversarialAuditResult(
                is_approved=bool(parsed.get("is_approved", False)),
                risk_score=int(parsed.get("risk_score", 5)),
                auditor_model=resp.model_name,
                auditor_provider=resp.provider,
                violations=list(parsed.get("violations", [])),
                critique=str(parsed.get("critique", "")),
                raw_response=resp.content,
            )
        except Exception as e:
            # Unparseable output fails closed
            return AdversarialAuditResult(
                is_approved=False,
                risk_score=10,
                auditor_model=resp.model_name,
                auditor_provider=resp.provider,
                violations=[f"Unparseable adversarial audit JSON: {e}"],
                critique="Auditor returned non-JSON response. Fails closed.",
                raw_response=resp.content,
            )
