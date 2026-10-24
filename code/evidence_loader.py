
import csv
import json
from pathlib import Path

DATASET = Path(__file__).resolve().parent.parent / "dataset"


def load_manifest():
    with (DATASET / "evidence_files.csv").open(
        encoding="utf-8-sig", newline=""
    ) as f:
        return list(csv.DictReader(f))


def load_json_evidence():
    results = []

    for entry in load_manifest():
        path = DATASET / entry["file_path"]

        if path.suffix.lower() != ".json":
            continue

        with path.open(encoding="utf-8-sig") as f:
            content = json.load(f)

        results.append({
            "evidence_id": entry["file_id"],
            "file_path": entry["file_path"],
            "captured_at": entry["captured_at"],
            "content": content
        })

    return results


def extract_json_records():
    extracted = []

    for evidence in load_json_evidence():
        content = evidence["content"]

        if not isinstance(content, dict):
            continue

        snapshots = content.get("snapshots", [])

        if not isinstance(snapshots, list):
            continue

        for snapshot in snapshots:
            if not isinstance(snapshot, dict):
                continue

            records = snapshot.get("records", [])

            if not isinstance(records, list):
                continue

            for record in records:
                if not isinstance(record, dict):
                    continue

                extracted.append({
                    "evidence_id": evidence["evidence_id"],
                    "system_id": snapshot.get("data_store"),
                    "collection": snapshot.get("collection"),
                    "captured_at": snapshot.get("captured_at"),
                    "record": record
                })

    return extracted

def extract_service_records():
    extracted = []

    for evidence in load_json_evidence():
        content = evidence["content"]

        if not isinstance(content, dict):
            continue

        service_exports = content.get("service_exports", {})

        if not isinstance(service_exports, dict):
            continue

        for system_id, collections in service_exports.items():
            if not isinstance(collections, dict):
                continue

            for collection, records in collections.items():
                if not isinstance(records, list):
                    continue

                for record in records:
                    if not isinstance(record, dict):
                        continue

                    extracted.append({
                        "evidence_id": evidence["evidence_id"],
                        "system_id": system_id,
                        "collection": collection,
                        "captured_at": record.get(
                            "observed_at",
                            evidence["captured_at"]
                        ),
                        "record": record
                    })

    return extracted


if __name__ == "__main__":
    records = extract_json_records()

    print("TOTAL EXTRACTED RECORDS:", len(records))

    print("\nFIRST RECORD:")

    if records:
        print(records[0])
