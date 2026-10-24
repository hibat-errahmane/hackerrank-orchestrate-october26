
import csv
from pathlib import Path
from collections import defaultdict

DATASET = Path(__file__).resolve().parent.parent / "dataset"

IDENTITY_FIELDS = ("email", "phone", "email_hash")


def load_csv(filename):
    with (DATASET / filename).open(
        encoding="utf-8-sig", newline=""
    ) as f:
        return list(csv.DictReader(f))


def normalize(value):
    return (value or "").strip().lower()


def resolve_identity(email, audit_at=None):
    identities = load_csv("user_identities.csv")
    history = load_csv("user_audit_log.csv")

    email = normalize(email)
    matching_ids = set()

    for user in identities:
        if normalize(user["email"]) == email:
            matching_ids.add(user["user_id"])

    for event in history:
        if event["field_name"] != "email":
            continue

        if audit_at and event["event_time"] > audit_at:
            continue

        if email in (
            normalize(event["old_value"]),
            normalize(event["new_value"])
        ):
            matching_ids.add(event["user_id"])

    results = []

    for user_id in sorted(matching_ids):
        identifiers = defaultdict(set)

        user = next(
            (u for u in identities if u["user_id"] == user_id),
            None
        )

        if user and (
            not audit_at or user["updated_at"] <= audit_at
        ):
            for field in IDENTITY_FIELDS:
                value = normalize(user.get(field))
                if value:
                    identifiers[field].add(value)

        for event in history:
            if event["user_id"] != user_id:
                continue

            if audit_at and event["event_time"] > audit_at:
                continue

            field = event["field_name"]

            if field in IDENTITY_FIELDS:
                for key in ("old_value", "new_value"):
                    value = normalize(event[key])
                    if value:
                        identifiers[field].add(value)

        results.append({
            "user_id": user_id,
            "emails": sorted(identifiers["email"]),
            "phones": sorted(identifiers["phone"]),
            "email_hashes": sorted(
                identifiers["email_hash"]
            )
        })

    return results


if __name__ == "__main__":
    result = resolve_identity(
        "nadia.ionescu@yahoo.com"
    )

    for user in result:
        print("USER:", user["user_id"])
        print("EMAILS:", user["emails"])
        print("PHONES:", user["phones"])
        print("HASHES:", user["email_hashes"])
