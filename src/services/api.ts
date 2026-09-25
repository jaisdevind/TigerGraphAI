import type { CaseSummaryItem, FullCaseAnswer } from "../types/case";

export async function getCaseList(): Promise<CaseSummaryItem[]> {
  const response = await api.get<CaseSummaryItem[]>("/api/cases");
  return response.data;
}


import axios from "axios";

export async function getCaseDetail(caseId: string): Promise<FullCaseAnswer> {
  const response = await api.get<FullCaseAnswer>(`/api/cases/${caseId}`);
  return response.data;
}

// Base URL for backend FastAPI server
const API_BASE_URL = "";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface InvestigationRequest {
  case_id: string;
  trigger_type: string;
  flagged_txn_id: string;
  customer_id: string;
  card_id: string;
  risk_score: number;
}

export interface RiskIndicators {
  source_risk_score: number;
  is_velocity_spike: boolean;
  is_new_device: boolean;
  is_new_region: boolean;
  is_mixed_channel: boolean;
  hard_linked_fraud_cases: number;
}

export interface EvidenceItem {
  evidence_id: string;
  claim: string;
  source_type: string;
  source_ref: string;
  entity_ids: string[];
  transaction_ids: string[];
  rule_id?: string | null;
  calculation?: string | null;
  timestamp: string;
}

export interface InvestigationResult {
  case_id: string;
  trigger_type: string;
  flagged_txn_id: string;
  customer_id: string;
  card_id: string;
  affected_txn_ids: string[];
  connected_card_ids: string[];
  connected_device_profiles: string[];
  detected_patterns: string[];
  risk_indicators: RiskIndicators;
  evidence: EvidenceItem[];
  related_cases: string[];
  similar_cases: string[];
  exposure_usd: number;
  uncertainty_factors: string[];
  missing_evidence: string[];
  investigation_status: string;
}

/* =========================
   Graph API Types
   ========================= */

export type GraphNodeType =
  | "customer"
  | "card"
  | "transaction"
  | "device"
  | "case";

export interface GraphNode {
  id: string;
  label: string;
  type: GraphNodeType;
  metadata: Record<string, string>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
}

export interface GraphResponse {
  case_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/* =========================
   Investigation API
   ========================= */

export async function investigate(
  request: InvestigationRequest,
): Promise<InvestigationResult> {
  const response = await api.post<InvestigationResult>(
    "/api/investigate",
    request,
  );

  return response.data;
}

/* =========================
   Health API
   ========================= */

export async function healthCheck(): Promise<{
  status: string;
  service: string;
}> {
  const response = await api.get("/health");

  return response.data;
}

/* =========================
   Graph API
   ========================= */

export async function getCaseGraph(
  caseId: string,
): Promise<GraphResponse> {
  const response = await api.get<GraphResponse>(
    `/api/cases/${caseId}/graph`,
  );

  return response.data;
};

// Trigger regeneration of all case investigations
export async function generateAllCases(): Promise<{status: string; generated_cases: number}> {
  const response = await api.post<{status: string; generated_cases: number}>(
    "/api/cases/generate-all",
  );
  return response.data;
}