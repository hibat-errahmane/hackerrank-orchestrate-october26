import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from policy_engine import evaluate_policy
from resource_assessor import assess_resource


class TestPolicyEngine(unittest.TestCase):

    def test_deleted_record(self):
        result = evaluate_policy("USER_PROFILE", "ABSENT")
        self.assertEqual(result["compliance_status"], "COMPLIANT")

    def test_remaining_record(self):
        result = evaluate_policy("USER_PROFILE", "PRESENT")
        self.assertEqual(result["compliance_status"], "NON_COMPLIANT")

    def test_missing_evidence(self):
        result = evaluate_policy("USER_PROFILE", "UNKNOWN")
        self.assertEqual(
            result["compliance_status"], "INSUFFICIENT_EVIDENCE"
        )

    def test_anonymized_analytics(self):
        result = evaluate_policy("ANALYTICS_PROFILE", "ANONYMIZED")
        self.assertEqual(result["compliance_status"], "COMPLIANT")

    def test_exposed_analytics(self):
        result = evaluate_policy("ANALYTICS_PROFILE", "PRESENT")
        self.assertEqual(result["compliance_status"], "NON_COMPLIANT")

    def test_redacted_support(self):
        result = evaluate_policy(
            "SUPPORT_MESSAGE", "REDACTED", condition_met=True
        )
        self.assertEqual(result["compliance_status"], "COMPLIANT")

    def test_support_condition_unknown(self):
        result = evaluate_policy("SUPPORT_MESSAGE", "REDACTED")
        self.assertEqual(
            result["compliance_status"], "INSUFFICIENT_EVIDENCE"
        )

    def test_security_retention(self):
        result = evaluate_policy(
            "SECURITY_AUDIT_LOG", "PRESENT", condition_met=True
        )
        self.assertEqual(result["compliance_status"], "COMPLIANT")

    def test_active_restore_risk(self):
        result = evaluate_policy(
            "BACKUP_ARCHIVE",
            "ACTIVE",
            condition_met=True,
            record_exists=True,
            restore_allowed=True
        )
        self.assertEqual(result["compliance_status"], "NON_COMPLIANT")

    def test_blocked_restore(self):
        result = evaluate_policy(
            "BACKUP_ARCHIVE",
            "BLOCKED",
            condition_met=True,
            record_exists=True,
            restore_allowed=False
        )
        self.assertEqual(result["compliance_status"], "COMPLIANT")


class TestRealEvidence(unittest.TestCase):

    def test_case_26_resources(self):
        resources = {
            "account_5684": ("USER_PROFILE", "COMPLIANT"),
            "analytics_4566": ("ANALYTICS_PROFILE", "COMPLIANT"),
            "backup_3120": ("BACKUP_ARCHIVE", "COMPLIANT"),
            "audit_record_5416": ("SECURITY_AUDIT_LOG", "COMPLIANT"),
            "support_4715": ("SUPPORT_MESSAGE", "INSUFFICIENT_EVIDENCE"),
            "data_flow_6244": ("DATA_FLOW", "COMPLIANT")
        }

        for resource_id, (category, expected) in resources.items():
            with self.subTest(resource=resource_id):
                result = assess_resource(
                    resource_id,
                    category,
                    "2026-09-15T12:00:00Z"
                )
                self.assertEqual(result["compliance_status"], expected)
                self.assertEqual(result["evidence_id"], "evidence_92")


if __name__ == "__main__":
    unittest.main()
