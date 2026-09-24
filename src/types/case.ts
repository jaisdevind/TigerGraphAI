export type CaseVerdict = "fraud" | "legitimate" | "uncertain";
export type CaseStatus = "open" | "closed_fraud" | "closed_legitimate" | "escalated";
export type FraudPattern =
  | "card_testing"
  | "card_not_present_fraud"
  | "card_not_present_new_device"
  | "out_of_region_use"
  | "account_takeover"
  | "undocumented"
  | "none";

export interface EvidenceItem {
  claim: string;
  source: "graph" | "document" | "customer" | "external";
  ref: string;
  entity_ids: string[];
}

export interface EvidenceRequest {
  type: "customer_validation" | "step_up_auth" | "analyst_info";
  asked_after_step: number;
  assumed_response: string;
}

export interface NextBestActionItem {
  action: string;
  route: "auto" | "L1" | "L2";
  reason: string;
}

export interface NextBestActions {
  initial: NextBestActionItem[];
  final: NextBestActionItem[];
  what_changed: string;
}

export interface SARReport {
  file: boolean;
  reason: string;
  narrative: string;
  subjects: string[];
  total_amount_usd: number;
  activity_dates: string[];
}

export interface CaseRecord {
  status: CaseStatus;
  verdict: CaseVerdict;
  fraud_probability: number;
  pattern: FraudPattern;
  pattern_description: string;
  affected_txn_ids: string[];
  first_suspicious_txn_id: string;
  connected_card_ids: string[];
  connected_device_profiles: string[];
  exposure_usd: number;
  evidence: EvidenceItem[];
  similar_prior_cases: string[];
  summary: string;
  written_to_graph: boolean;
  graph_case_id: string;
}

export interface FullCaseAnswer {
  case_id: string;
  case: CaseRecord;
  evidence_requests: EvidenceRequest[];
  next_best_actions: NextBestActions;
  sar: SARReport;
  stop_reason: string;
  tool_calls: number;
  tokens: number;
  latency_s: number;
}

export interface CaseSummaryItem {
  case_id: string;
  customer_id: string;
  card_id: string;
  flagged_txn_id: string;
  trigger_type: string;
  trigger_text: string;
  status: CaseStatus;
  verdict: CaseVerdict;
  pattern: FraudPattern;
  exposure_usd: number;
  sar_filed: boolean;
  fraud_probability: number;
}
