
from temporal_engine import (
    get_resource_timeline,
    interpret_state,
    parse_time,
)
from policy_engine import evaluate_policy


def assess_resource(resource_id, data_category, audit_at):
    timeline = get_resource_timeline(resource_id, audit_at)

    if not timeline:
        return {
            "resource_id": resource_id,
            "data_category": data_category,
            "system_id": None,
            "observed_state": "UNKNOWN",
            "compliance_status": "INSUFFICIENT_EVIDENCE",
            "evidence_id": None,
            "reason": "No admissible evidence found.",
        }

    latest = timeline[-1]
    record = latest["record"]
    state = interpret_state(latest)

    if data_category == "DATA_FLOW":
        if state == "DISABLED":
            compliance = "COMPLIANT"
        elif state == "ACTIVE":
            compliance = "NON_COMPLIANT"
        else:
            compliance = "INSUFFICIENT_EVIDENCE"

        decision = {
            "required_action": "DISABLE_DATA_FLOW",
            "compliance_status": compliance,
            "reason": "Data-flow state assessment.",
        }

    else:
        kwargs = {}

        if data_category == "SECURITY_AUDIT_LOG":
            deadline = parse_time(record.get("retention_until"))
            cutoff = parse_time(audit_at)

            kwargs["condition_met"] = (
                deadline > cutoff if deadline else None
            )

        elif data_category == "BACKUP_ARCHIVE":
            restore = record.get("restore_allowed")

            kwargs["condition_met"] = (
                True if type(restore) is bool else None
            )

            kwargs["record_exists"] = (
                True if record.get("archive_key")
                or record.get("archive_path")
                else None
            )

            kwargs["restore_allowed"] = (
                restore if type(restore) is bool else None
            )

        elif data_category in (
            "SUPPORT_MESSAGE",
            "ACCOUNT_TOMBSTONE",
            "LEGAL_HOLD_RECORD",
        ):
            # Additional contextual evidence is required.
            kwargs["condition_met"] = None

        decision = evaluate_policy(
            data_category,
            state,
            **kwargs
        )

    return {
        "resource_id": resource_id,
        "system_id": latest["system_id"],
        "data_category": data_category,
        "required_action": decision["required_action"],
        "observed_state": state,
        "compliance_status": decision["compliance_status"],
        "evidence_id": latest["evidence_id"],
        "reason": decision["reason"],
    }
