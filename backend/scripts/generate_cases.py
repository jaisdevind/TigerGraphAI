"""
Batch Runner for TigerGraphAI.
Iterates through all 20 cases in dataset/case_pack.csv, runs the investigation pipeline,
validates the answer structure against the Hackathon Answer Format,
and saves the 20 files into cases/<case_id>.json.
"""

import csv
import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.agentic_pipeline import AgenticInvestigationPipeline
from backend.services.graph_store import GraphStore


def validate_case_answer(data: dict) -> None:
    """
    Validates that the generated dictionary strictly matches the Hackathon format.
    """
    assert "case_id" in data, "Missing top-level case_id"
    assert "case" in data, "Missing case object"
    assert "evidence_requests" in data, "Missing evidence_requests list"
    assert "next_best_actions" in data, "Missing next_best_actions object"
    assert "sar" in data, "Missing sar object"
    assert "stop_reason" in data, "Missing stop_reason"
    assert "tool_calls" in data, "Missing tool_calls"
    assert "tokens" in data, "Missing tokens"
    assert "latency_s" in data, "Missing latency_s"

    case = data["case"]
    assert case["status"] in ("open", "closed_fraud", "closed_legitimate", "escalated")
    assert case["verdict"] in ("fraud", "legitimate", "uncertain")
    assert 0.0 <= case["fraud_probability"] <= 1.0
    assert case["pattern"] in (
        "card_testing",
        "card_not_present_fraud",
        "card_not_present_new_device",
        "out_of_region_use",
        "account_takeover",
        "undocumented",
        "none",
    )
    if case["pattern"] == "undocumented":
        assert len(case["pattern_description"]) > 10, "pattern_description required for undocumented"
    else:
        assert case["pattern_description"] == ""

    if case["verdict"] == "legitimate":
        assert case["affected_txn_ids"] == [], "affected_txn_ids must be [] for legitimate"
        assert case["exposure_usd"] == 0.0, "exposure_usd must be 0 for legitimate"
        assert data["sar"]["file"] is False, "sar.file must be False for legitimate"

    sar = data["sar"]
    if not sar["file"]:
        assert sar["narrative"] == "", "sar.narrative must be '' when file is false"
        assert sar["subjects"] == [], "sar.subjects must be [] when file is false"
        assert sar["total_amount_usd"] == 0, "sar.total_amount_usd must be 0 when file is false"
        assert sar["activity_dates"] == [], "sar.activity_dates must be [] when file is false"
    else:
        assert len(sar["narrative"]) > 50, "sar.narrative must be comprehensive when file is true"
        assert len(sar["activity_dates"]) == 2, "sar.activity_dates must have start and end date"

    nba = data["next_best_actions"]
    assert "initial" in nba and isinstance(nba["initial"], list)
    assert "final" in nba and isinstance(nba["final"], list)
    assert "what_changed" in nba


def generate_all_cases() -> None:
    cases_dir = PROJECT_ROOT / "cases"
    cases_dir.mkdir(exist_ok=True)

    case_pack_file = PROJECT_ROOT / "dataset" / "case_pack.csv"
    if not case_pack_file.exists():
        raise FileNotFoundError(f"Case pack file not found at {case_pack_file}")

    graph_store = GraphStore()
    pipeline = AgenticInvestigationPipeline(graph_store=graph_store)

    cases = []
    with open(case_pack_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cases.append(row)

    print(f"Loaded {len(cases)} cases from {case_pack_file.name}. Commencing investigation...")

    results = []
    for idx, trigger in enumerate(cases, 1):
        case_id = trigger["case_id"]
        print(f"[{idx}/{len(cases)}] Investigating {case_id} (Trigger: {trigger['trigger_type']})...")
        answer = pipeline.run_investigation(trigger)
        validate_case_answer(answer)

        # Write to cases/<case_id>.json
        out_path = cases_dir / f"{case_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(answer, f, indent=2)

        results.append(answer)

    print(f"\nSuccessfully generated and validated {len(results)} answer files in {cases_dir}!")


if __name__ == "__main__":
    generate_all_cases()
