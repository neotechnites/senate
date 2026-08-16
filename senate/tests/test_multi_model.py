"""Unit tests for Multi-Model Gateway and Adversarial Auditor in The Senate."""

import json
import unittest
from unittest.mock import MagicMock

from senate.models.adversary import MultiModelAdversary
from senate.models.gateway import ModelGateway, ModelProvider, ModelResponse


class TestMultiModelEngine(unittest.TestCase):
    def test_mock_adversarial_audit_rejection(self):
        """Verify that adversarial auditor catches invariant breaches and rejects proposal."""
        mock_gateway = MagicMock(spec=ModelGateway)
        mock_gateway.query.return_value = ModelResponse(
            content=json.dumps({
                "is_approved": False,
                "risk_score": 9,
                "violations": ["Proposal allocates $150, exceeding $100 budget cap."],
                "critique": "The proposal ignores the hard capital cap.",
            }),
            provider="google",
            model_name="gemini-1.5-pro",
            duration_s=0.5,
            usage_tokens={"input": 100, "output": 50},
        )

        adversary = MultiModelAdversary(mock_gateway)
        result = adversary.audit_proposal(
            proposal_description="Deploy $150 to high-yield lane",
            invariants_list=["Capital allocation must be <= $100.00"],
            auditor_provider=ModelProvider.GOOGLE,
            auditor_model="gemini-1.5-pro",
        )

        self.assertFalse(result.is_approved)
        self.assertEqual(result.risk_score, 9)
        self.assertEqual(result.auditor_provider, "google")
        self.assertTrue(any("exceeding $100" in v for v in result.violations))

    def test_mock_adversarial_audit_approval(self):
        """Verify that adversarial auditor approves proposal when invariants pass."""
        mock_gateway = MagicMock(spec=ModelGateway)
        mock_gateway.query.return_value = ModelResponse(
            content=json.dumps({
                "is_approved": True,
                "risk_score": 1,
                "violations": [],
                "critique": "All invariant predicates satisfied.",
            }),
            provider="openai",
            model_name="gpt-4o",
            duration_s=0.4,
            usage_tokens={"input": 120, "output": 30},
        )

        adversary = MultiModelAdversary(mock_gateway)
        result = adversary.audit_proposal(
            proposal_description="Deploy $49.94 to ballot measure market maker",
            invariants_list=["Capital allocation must be <= $100.00"],
            auditor_provider=ModelProvider.OPENAI,
            auditor_model="gpt-4o",
        )

        self.assertTrue(result.is_approved)
        self.assertEqual(result.risk_score, 1)
        self.assertEqual(len(result.violations), 0)

    def test_adversary_fails_closed_on_error(self):
        """Verify that if auditor call encounters an error or network drop, it FAILS CLOSED."""
        mock_gateway = MagicMock(spec=ModelGateway)
        mock_gateway.query.return_value = ModelResponse(
            content="",
            provider="google",
            model_name="gemini-1.5-pro",
            duration_s=0.1,
            usage_tokens={},
            is_error=True,
            error_message="Network timeout to API endpoint",
        )

        adversary = MultiModelAdversary(mock_gateway)
        result = adversary.audit_proposal(
            proposal_description="Any proposal",
            invariants_list=["Rule 1"],
        )

        self.assertFalse(result.is_approved)
        self.assertEqual(result.risk_score, 10)
        self.assertTrue(any("Fails closed" in v for v in result.violations))


if __name__ == "__main__":
    unittest.main()
