import axios from "axios";
import type { CaseSummaryItem, FullCaseAnswer } from "../types/case";

const API_BASE_URL = "http://127.0.0.1:8000";

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

export async function getCaseList(): Promise<CaseSummaryItem[]> {
  const response = await api.get<CaseSummaryItem[]>("/api/cases");
  return response.data;
}

export async function getCaseDetail(caseId: string): Promise<FullCaseAnswer> {
  const response = await api.get<FullCaseAnswer>(`/api/cases/${caseId}`);
  return response.data;
}

export async function getCaseGraph(caseId: string): Promise<GraphResponse> {
  const response = await api.get<GraphResponse>(`/api/cases/${caseId}/graph`);
  return response.data;
}

export async function investigate(
  request: InvestigationRequest,
): Promise<any> {
  const response = await api.post("/api/investigate", request);
  return response.data;
}

export async function generateAllCases(): Promise<{ status: string; generated_cases: number }> {
  const response = await api.post("/api/cases/generate-all");
  return response.data;
}

export async function healthCheck(): Promise<{
  status: string;
  service: string;
}> {
  const response = await api.get<{
    status: string;
    service: string;
  }>("/health");

  return response.data;
}
