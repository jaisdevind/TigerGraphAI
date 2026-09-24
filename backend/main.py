"""
TigerGraphAI Investigation API.
FastAPI application serving:
- Health check
- Case listings (/api/cases)
- Case investigation details & SAR records (/api/cases/{case_id})
- Graph visual subgraphs (/api/cases/{case_id}/graph)
- Single trigger investigation (/api/investigate)
- Full 20-case batch runner trigger (/api/cases/generate-all)
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.services.agentic_pipeline import AgenticInvestigationPipeline
from backend.services.config import PatternRuleConfig
from backend.services.graph_models import GraphResponse
from backend.services.graph_service import CaseGraphService
from backend.services.graph_store import GraphStore
from backend.services.investigation_engine import (
    DeterministicFraudEngine,
    InvestigationResult,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = PROJECT_ROOT / "cases"
CASES_DIR.mkdir(exist_ok=True)
CASE_PACK_CSV = PROJECT_ROOT / "dataset" / "case_pack.csv"


class InvestigationRequest(BaseModel):
    case_id: str = "HHG-001"
    trigger_type: str = "risk_score"
    flagged_txn_id: str
    customer_id: str
    card_id: str
    risk_score: float = 0.0


# Initialize shared services
graph_store = GraphStore()
case_graph_service = CaseGraphService(graph_client=graph_store)

rule_config = PatternRuleConfig(
    P1_SMALL_AUTH_THRESHOLD=5.0,
    P5_MIXED_CHANNEL_HOURS=24,
)
deterministic_engine = DeterministicFraudEngine(
    graph_client=graph_store,
    config=rule_config,
)
pipeline = AgenticInvestigationPipeline(graph_store=graph_store)


app = FastAPI(
    title="TigerGraphAI Fraud Investigation API",
    description="Deterministic and Agentic fraud investigation API for IEEE-CIS / Hacker House Goa",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_case_pack() -> Dict[str, Dict[str, Any]]:
    case_map = {}
    if CASE_PACK_CSV.exists():
        with open(CASE_PACK_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                case_map[row["case_id"]] = row
    return case_map


@app.get("/health")
def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "TigerGraphAI Fraud Investigation Platform",
        "version": "1.0.0",
    }


@app.get("/api/cases")
def list_cases() -> List[Dict[str, Any]]:
    """
    Returns list of all 20 cases with their triggers and current status.
    """
    case_pack = _load_case_pack()
    results = []

    for case_id, trigger in case_pack.items():
        case_file = CASES_DIR / f"{case_id}.json"
        if case_file.exists():
            try:
                with open(case_file, "r", encoding="utf-8") as f:
                    case_data = json.load(f)
                results.append({
                    "case_id": case_id,
                    "customer_id": trigger["customer_id"],
                    "card_id": trigger["card_id"],
                    "flagged_txn_id": trigger["flagged_txn_id"],
                    "trigger_type": trigger["trigger_type"],
                    "trigger_text": trigger.get("trigger_text", ""),
                    "status": case_data["case"]["status"],
                    "verdict": case_data["case"]["verdict"],
                    "pattern": case_data["case"]["pattern"],
                    "exposure_usd": case_data["case"]["exposure_usd"],
                    "sar_filed": case_data["sar"]["file"],
                    "fraud_probability": case_data["case"]["fraud_probability"],
                })
                continue
            except Exception:
                pass

        # If file not present yet, return trigger summary
        results.append({
            "case_id": case_id,
            "customer_id": trigger["customer_id"],
            "card_id": trigger["card_id"],
            "flagged_txn_id": trigger["flagged_txn_id"],
            "trigger_type": trigger["trigger_type"],
            "trigger_text": trigger.get("trigger_text", ""),
            "status": "open",
            "verdict": "uncertain",
            "pattern": "none",
            "exposure_usd": 0.0,
            "sar_filed": False,
            "fraud_probability": 0.0,
        })

    return results


@app.get("/api/cases/{case_id}")
def get_case_detail(case_id: str) -> Dict[str, Any]:
    """
    Returns the complete 3-part investigation answer for a case.
    """
    case_file = CASES_DIR / f"{case_id}.json"
    if case_file.exists():
        with open(case_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # If file not yet on disk, run dynamically
    case_pack = _load_case_pack()
    if case_id in case_pack:
        answer = pipeline.run_investigation(case_pack[case_id])
        with open(case_file, "w", encoding="utf-8") as f:
            json.dump(answer, f, indent=2)
        return answer

    raise HTTPException(status_code=404, detail=f"Case '{case_id}' was not found.")


@app.get(
    "/api/cases/{case_id}/graph",
    response_model=GraphResponse,
)
def get_case_graph(case_id: str) -> GraphResponse:
    """
    Return the graph representation for an investigation case.
    """
    case_pack = _load_case_pack()
    if case_id in case_pack:
        trigger = case_pack[case_id]
        return case_graph_service.build_case_graph(
            case_id=case_id,
            customer_id=trigger["customer_id"],
            card_id=trigger["card_id"],
            transaction_id=trigger["flagged_txn_id"],
        )

    # Fallback for development CASE-001
    if case_id == "CASE-001":
        return case_graph_service.build_case_graph(
            case_id="CASE-001",
            customer_id="CUSTOMER-001",
            card_id="CARD-001",
            transaction_id="TXN-001",
        )

    raise HTTPException(
        status_code=404,
        detail=f"Case '{case_id}' was not found.",
    )


@app.post(
    "/api/investigate",
    response_model=InvestigationResult,
)
def investigate(request: InvestigationRequest) -> InvestigationResult:
    trigger = {
        "case_id": request.case_id,
        "trigger_type": request.trigger_type,
        "flagged_txn_id": request.flagged_txn_id,
        "customer_id": request.customer_id,
        "card_id": request.card_id,
        "risk_score": request.risk_score,
    }

    try:
        return deterministic_engine.investigate(trigger)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Investigation failed: {exc}"
        ) from exc


@app.post("/api/cases/generate-all")
def generate_all() -> Dict[str, Any]:
    """
    Regenerates and validates all 20 case files.
    """
    case_pack = _load_case_pack()
    count = 0
    for case_id, trigger in case_pack.items():
        answer = pipeline.run_investigation(trigger)
        out_path = CASES_DIR / f"{case_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(answer, f, indent=2)
        count += 1

    return {"status": "success", "generated_cases": count}
