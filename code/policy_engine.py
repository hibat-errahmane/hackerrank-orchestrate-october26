
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
