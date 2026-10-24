
from datetime import datetime, timezone

from evidence_loader import (
    extract_json_records,
    extract_service_records
)


def parse_time(value):
    if not value:
        return None

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).astimezone(timezone.utc)


def get_resource_timeline(resource_id, audit_at):
    cutoff = parse_time(audit_at)

    observations = (
        extract_json_records()
        + extract_service_records()
    )

    timeline = []

    for item in observations:
        record = item["record"]

        if record.get("resource_id") != resource_id:
            continue

        observed_at = parse_time(item["captured_at"])

        if observed_at is None or observed_at > cutoff:
            continue

        timeline.append(item)

    timeline.sort(
    key=lambda x: (
        parse_time(x["captured_at"]),
        1 if x["collection"] in (
            "profile_lookups",
            "profiles",
            "restore_entries",
            "connectors",
            "audit_records",
            "tickets",
            "index_queries",
            "exports"
        ) else 0
    )
)

    return timeline



def interpret_state(observation):
    record = observation["record"]
    system = observation["system_id"]
    collection = observation["collection"]

    if system == "account_service":
        if (
            record.get("status_code") == 404
            and "profile" in record
            and record["profile"] is None
        ):
            return "ABSENT"

        if record.get("account_status") == "ACTIVE":
            return "PRESENT"

        if record.get("profile") is not None:
            return "PRESENT"

    if system == "analytics_platform":
        identifier_fields = (
            "user_id",
            "customer_reference",
            "email",
            "phone",
            "email_hash"
        )

        present_fields = [
            field for field in identifier_fields
            if field in record
        ]

        if (
            present_fields
            and all(record[field] is None for field in present_fields)
            and (
                "user_id" in record
                or "customer_reference" in record
            )
        ):
            return "ANONYMIZED"

        if any(
            record.get(field) is not None
            for field in present_fields
        ):
            return "PRESENT"

    if system == "integration_service":
        if record.get("enabled") is False:
            return "DISABLED"
        if record.get("enabled") is True:
            return "ACTIVE"

    if system == "backup_service":
        if record.get("restore_allowed") is False:
            return "BLOCKED"
        if record.get("restore_allowed") is True:
            return "ACTIVE"

    if system == "support_platform":
        direct_fields = (
            "requester_name",
            "requester_email",
            "requester_phone"
        )

        if (
            any(field in record for field in direct_fields)
            and all(
                record.get(field) is None
                for field in direct_fields
            )
        ):
            return "REDACTED"

        if record.get("message_text") == "[REDACTED]":
            return "REDACTED"

    if system == "security_service":
        if record.get("resource_id"):
            return "PRESENT"

    return "UNKNOWN"


def select_verification_evidence(resource_id, audit_at):
    timeline = get_resource_timeline(resource_id, audit_at)

    if not timeline:
        return None

    verified = []

    for observation in timeline:
        state = interpret_state(observation)

        if state == "UNKNOWN":
            continue

        is_direct = observation["collection"] in {
            "profile_lookups",
            "profiles",
            "restore_entries",
            "connectors",
            "audit_records",
            "tickets",
            "index_queries",
            "exports",
        }

        verified.append((
            observation,
            state,
            is_direct
        ))

    if not verified:
        return None

    # Prefer a direct readback when it is available.
    # This is provisional and must later be checked
    # for contradictory, newer observations.
    verified.sort(
        key=lambda item: (
            item[2],
            parse_time(item[0]["captured_at"])
        )
    )

    observation, state, _ = verified[-1]

    return {
        "resource_id": resource_id,
        "state": state,
        "evidence_id": observation["evidence_id"],
        "observed_at": observation["captured_at"],
        "system_id": observation["system_id"]
    }


if __name__ == "__main__":
    timeline = get_resource_timeline(
        "account_5684",
        "2026-09-15T12:00:00Z"
    )

    print("OBSERVATIONS:", len(timeline))

    for item in timeline:
        print(
            item["captured_at"],
            item["evidence_id"],
            item["record"]
        )

    if timeline:
        latest = timeline[-1]

        print("\nLATEST OBSERVATION:")
        print(latest)
