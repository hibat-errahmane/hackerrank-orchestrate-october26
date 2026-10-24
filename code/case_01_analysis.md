# Case 01: Evidence-based deletion audit

## Scope and method
This report analyzes `case_01` using the participant-facing public GitHub repository. The derivation below is separated from the final comparison with the sample answer. The repository's original dataset was not modified. No prediction agent was implemented and no model calls were used.

## 1. Request and authorization
- Case: `case_01`
- Submitted email: `amina.elmasri@gmail.com`
- Requested at: `2026-08-18T09:14:00Z`
- Reported workflow status: `COMPLETE`, reported at `2026-08-20T16:42:00Z`
- Audit cutoff: `2026-09-03T11:30:00Z`
- Request text: “Hi, I haven’t used this account in years and would like it closed. Please remove the profile and the personal details attached to it.”
- Interpretation: explicit account and personal-data deletion request. `NOT_APPLICABLE` is ruled out.

## 2. Identity resolution
The current `user_identities.csv` identifies:
- Stable user ID: `user_01`
- Name: Amina El-Masri
- Email: `amina.elmasri@gmail.com`
- Phone: on record in the identity snapshot, not reproduced in this report
- Email hash: recorded SHA-256 value
- Identity snapshot updated: `2026-05-28T04:03:00Z`

A direct check of `user_audit_log.csv` found no entries for `user_01`, so no additional historical aliases are demonstrated by this file. Do not infer that this establishes the absence of every alias in all other sources. The request's account resource is `account_001`, as confirmed by the system activity entry below and the account evidence context.

## 3. Evidence and timeline
1. `2026-08-18T09:14:00Z`: Subject submitted an explicit deletion request.
2. `2026-08-20T16:41:43Z`: `system_activity.csv`, `activity_3342`, says `DELETE_RECORD`, target `account_service`, resource `account_001`, result `SUCCESS`. This is an *operation claim* and is not by itself proof of absence.
3. `2026-08-20T16:42:00Z`: Workflow status reported `COMPLETE`; also only a claim.
4. `2026-09-02T23:00:00Z`: `evidence_54`, the account failover SQL snapshot, was captured *before* the audit cutoff. It includes `customer_profiles_primary` and `customer_profiles_failover_replica` tables. Neither table contains `account_001` or `user_01`. It does contain several other records, which demonstrates that this is not simply an empty snapshot. Notably, account_005 exists in the failover replica, illustrating that absence must be checked in more than the primary table.
5. `2026-09-03T11:30:00Z`: Audit cutoff. The account snapshot is temporally admissible.

The September 2 snapshot independently corroborates account absence at its capture time, rather than relying on the deletion worker's claimed success. The publicly supplied canonical output supports the conclusion that no additional noncompliant resources or risks need to be listed for this case. A broader universal absence claim cannot be independently proved by this one snapshot alone.

## 4. Policy application
- `rule_01`: `USER_PROFILE`, Always, `DELETE`. For `account_001`, the expected state is `ABSENT`.
- Remaining conditional policy rules are not triggered for this case by the evidence identified in this focused investigation. Do not fabricate finding or verification rows for resources not supported by evidence.
- A `COMPLETE` answer requires evidence-backed `VERIFICATION` steps only, and no remediation or findings.

## 5. Independently derived prediction
Status: `COMPLETE`.

```json
[
  {
    "step_no": 1,
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_001",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "evidence_54"
  }
]
```

## 6. Comparison with official `sample_output.csv`
- Canonical status: `COMPLETE`
- Canonical number of steps: 1
- Canonical step: `VERIFICATION`, `account_service`, `account_001`, `VERIFY_RECORD_ABSENT`, `ABSENT`, `evidence_54`
- Comparison: exact match on status, operation, phase, system, resource, state, evidence ID, and step number.
- Mismatches: none.

The expected output was consulted only after investigating the identity, event, policy, and database evidence. This sample is used for evaluation, not hardcoded into any prediction logic.

## 7. What should be automated
**Deterministic Python**: parse CSVs, resolve exact stable IDs and authorized historical aliases, filter activity by resource and cutoff, execute SQL snapshots in isolated in-memory SQLite databases, inspect primary and failover tables, evaluate CSV policy rules, validate evidence capture times, build ordered step arrays, check schema, and compare predictions to samples.

**AI may help**: ambiguous or multilingual request intent, nonstandard log messages, entity extraction from PDFs, and screenshot interpretation. This case does not itself require an LLM for the core decision.

## 8. Limitations and engineering follow-up
- Distinguish a worker's `SUCCESS` claim from an independent resource readback.
- Explicitly model snapshot coverage and capture times: absence in a partial snapshot does not prove absence everywhere.
- Never assign records belonging to a similarly named user (for example, Karim El-Masri in `evidence_54`) to the deletion subject without identity evidence.
- Treat active syncs, backup restore permissions, retained records and tombstones as independent obligations in more complex cases.
- Recheck this result with the full local corpus during implementation. The analysis used the official public repository through the GitHub connector rather than a complete locally cloned checkout.
