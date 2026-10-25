
import csv
from pathlib import Path

DATASET = Path(__file__).resolve().parent.parent / "dataset"


def load_deletion_rules():
    path = DATASET / "deletion_rules.csv"

    with path.open(
        encoding="utf-8-sig",
        newline=""
    ) as f:
        return list(csv.DictReader(f))


def get_policy(data_category):
    rules = load_deletion_rules()

    matches = [
        rule for rule in rules
        if rule["data_category"] == data_category
    ]

    return matches


def evaluate_policy(
    data_category,
    observed_state,
    condition_met=None,
    record_exists=None,
    restore_allowed=None
):
    """
    Evaluate whether a resource satisfies its deletion policy.

    Returns a structured decision.
    Unknown evidence never proves compliance.
    """
    rules = get_policy(data_category)

    if not rules:
        return {
            "data_category": data_category,
            "required_action": None,
            "observed_state": observed_state,
            "compliance_status": "INSUFFICIENT_EVIDENCE",
            "reason": "No matching deletion policy found."
        }

    rule = rules[0]
    required_action = rule["required_action"]

    if required_action == "DELETE":
        if observed_state == "ABSENT":
            compliance_status = "COMPLIANT"
            reason = "The record is confirmed absent."
        elif observed_state == "PRESENT":
            compliance_status = "NON_COMPLIANT"
            reason = "The record still exists."
        else:
            compliance_status = "INSUFFICIENT_EVIDENCE"
            reason = "The available evidence does not establish absence or presence."

    
    elif required_action == "ANONYMIZE":
        if observed_state == "ANONYMIZED":
            compliance_status = "COMPLIANT"
            reason = "The record is confirmed anonymized."

        elif observed_state == "PRESENT":
            compliance_status = "NON_COMPLIANT"
            reason = "The record still contains attributable personal data."

        else:
            compliance_status = "INSUFFICIENT_EVIDENCE"
            reason = "Anonymization could not be verified."

    
    elif required_action == "REDACT":
        if condition_met is not True:
            compliance_status = "INSUFFICIENT_EVIDENCE"
            reason = (
                "The policy condition has not been established, "
                "or no fallback treatment is defined."
            )

        elif observed_state == "REDACTED":
            compliance_status = "COMPLIANT"
            reason = (
                "The required identifying information "
                "has been verified as redacted."
            )

        elif observed_state == "EXPOSED_PII":
            compliance_status = "NON_COMPLIANT"
            reason = (
                "The record still exposes identifiers "
                "that policy requires to be removed."
            )

        else:
            compliance_status = "INSUFFICIENT_EVIDENCE"
            reason = (
                "The evidence does not establish whether "
                "the required redaction is complete."
            )

    
    elif required_action == "RETAIN":

        if condition_met is not True:
            compliance_status = "INSUFFICIENT_EVIDENCE"
            reason = (
                "The retention condition is not established "
                "or no fallback policy is specified."
            )

        elif data_category == "BACKUP_ARCHIVE":

            if record_exists is False and restore_allowed is True:
                compliance_status = "INSUFFICIENT_EVIDENCE"
                reason = "Contradictory archive and restore evidence."

            elif record_exists is False:
                compliance_status = "NON_COMPLIANT"
                reason = "The required archive is missing."

            elif record_exists is True and restore_allowed is True:
                compliance_status = "NON_COMPLIANT"
                reason = "The archive can still restore personal data."

            elif record_exists is True and restore_allowed is False:
                compliance_status = "COMPLIANT"
                reason = (
                    "The archive is preserved and restore access "
                    "is confirmed blocked."
                )

            else:
                compliance_status = "INSUFFICIENT_EVIDENCE"
                reason = (
                    "Archive existence or restore permissions "
                    "could not be verified."
                )

        elif data_category in (
            "SECURITY_AUDIT_LOG",
            "LEGAL_HOLD_RECORD"
        ):

            if observed_state == "PRESENT":
                compliance_status = "COMPLIANT"
                reason = "The required retained record exists."

            elif observed_state == "ABSENT":
                compliance_status = "NON_COMPLIANT"
                reason = "A required retained record is missing."

            else:
                compliance_status = "INSUFFICIENT_EVIDENCE"
                reason = "Retention could not be verified."

        else:
            compliance_status = "INSUFFICIENT_EVIDENCE"
            reason = "Unsupported retention category."

    else:
        compliance_status = "INSUFFICIENT_EVIDENCE"
        reason = "Conditional policy evaluation is not implemented yet."




    return {
        "data_category": data_category,
        "required_action": required_action,
        "observed_state": observed_state,
        "compliance_status": compliance_status,
        "reason": reason
    }

if __name__ == "__main__":
    rules = load_deletion_rules()

    print("TOTAL RULES:", len(rules))

    for rule in rules:
        print(
            rule["data_category"],
            "=>",
            rule["required_action"],
            "| CONDITION:",
            rule["condition"]
        )
