import { useEffect, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Copy,
  Database,
  FileCheck,
  FileSearch,
  Fingerprint,
  Network,
  Shield,
} from "lucide-react";
import { getCaseDetail, getCaseList } from "../services/api";
import type { FullCaseAnswer, CaseSummaryItem } from "../types/case";

interface CaseInvestigationProps {
  currentCaseId: string;
  onCaseChange: (caseId: string) => void;
  onOpenGraph: (caseId: string) => void;
}

export default function CaseInvestigation({
  currentCaseId,
  onCaseChange,
  onOpenGraph,
}: CaseInvestigationProps) {
  const [caseList, setCaseList] = useState<CaseSummaryItem[]>([]);
  const [data, setData] = useState<FullCaseAnswer | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    getCaseList().then(setCaseList).catch(console.error);
  }, []);

  useEffect(() => {
    async function loadCase() {
      try {
        setLoading(true);
        setError("");
        const res = await getCaseDetail(currentCaseId);
        setData(res);
      } catch (err: any) {
        setError(err.message || "Failed to load case details.");
      } finally {
        setLoading(false);
      }
    }
    loadCase();
  }, [currentCaseId]);

  const handleCopyNarrative = () => {
    if (data?.sar?.narrative) {
      navigator.clipboard.writeText(data.sar.narrative);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const currentIndex = caseList.findIndex((c) => c.case_id === currentCaseId);
  const prevCase = currentIndex > 0 ? caseList[currentIndex - 1].case_id : null;
  const nextCase = currentIndex < caseList.length - 1 ? caseList[currentIndex + 1].case_id : null;

  if (loading) {
    return (
      <div style={{ padding: "3rem", textAlign: "center", color: "#64748b" }}>
        Loading case {currentCaseId}...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div style={{ padding: "2rem", color: "#ef4444" }}>
        Failed to load case: {error}
      </div>
    );
  }

  const { case: c, evidence_requests, next_best_actions, sar } = data;
  const isFraud = c.verdict === "fraud";

  return (
    <div style={{ padding: "1.5rem", maxWidth: "1280px", margin: "0 auto" }}>
      {/* Top Bar Navigation */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          <select
            value={currentCaseId}
            onChange={(e) => onCaseChange(e.target.value)}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "0.5rem",
              border: "1px solid #cbd5e1",
              fontWeight: 700,
              fontSize: "1rem",
              color: "#0f172a",
              backgroundColor: "white",
              cursor: "pointer",
            }}
          >
            {caseList.map((item) => (
              <option key={item.case_id} value={item.case_id}>
                {item.case_id} — {item.verdict.toUpperCase()} ({item.pattern === "none" ? "Legitimate" : item.pattern})
              </option>
            ))}
          </select>

          <div style={{ display: "flex", gap: "0.25rem" }}>
            <button
              disabled={!prevCase}
              onClick={() => prevCase && onCaseChange(prevCase)}
              style={{
                padding: "0.4rem 0.6rem",
                borderRadius: "0.375rem",
                border: "1px solid #cbd5e1",
                background: prevCase ? "white" : "#f1f5f9",
                cursor: prevCase ? "pointer" : "not-allowed",
              }}
            >
              <ArrowLeft size={16} />
            </button>
            <button
              disabled={!nextCase}
              onClick={() => nextCase && onCaseChange(nextCase)}
              style={{
                padding: "0.4rem 0.6rem",
                borderRadius: "0.375rem",
                border: "1px solid #cbd5e1",
                background: nextCase ? "white" : "#f1f5f9",
                cursor: nextCase ? "pointer" : "not-allowed",
              }}
            >
              <ArrowRight size={16} />
            </button>
          </div>
        </div>

        <button
          onClick={() => onOpenGraph(currentCaseId)}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            backgroundColor: "#4f46e5",
            color: "white",
            padding: "0.5rem 1rem",
            borderRadius: "0.5rem",
            border: "none",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          <Network size={16} /> Open in Graph Explorer
        </button>
      </div>

      {/* Case Header Card */}
      <div
        style={{
          background: "white",
          borderRadius: "0.75rem",
          padding: "1.25rem",
          border: `1px solid ${isFraud ? "#fca5a5" : "#86efac"}`,
          borderLeft: `6px solid ${isFraud ? "#ef4444" : "#10b981"}`,
          marginBottom: "1.5rem",
          boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <h2 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 700, color: "#0f172a" }}>
                Case {currentCaseId}
              </h2>
              <span
                style={{
                  padding: "0.25rem 0.75rem",
                  borderRadius: "9999px",
                  fontSize: "0.8rem",
                  fontWeight: 700,
                  backgroundColor: isFraud ? "#fee2e2" : "#dcfce7",
                  color: isFraud ? "#b91c1c" : "#15803d",
                }}
              >
                {c.verdict.toUpperCase()} (Prob: {(c.fraud_probability * 100).toFixed(0)}%)
              </span>
              <span
                style={{
                  padding: "0.25rem 0.5rem",
                  borderRadius: "0.25rem",
                  fontSize: "0.75rem",
                  fontWeight: 600,
                  backgroundColor: "#f1f5f9",
                  color: "#475569",
                }}
              >
                STATUS: {c.status}
              </span>
              {c.written_to_graph && (
                <span
                  style={{
                    padding: "0.25rem 0.5rem",
                    borderRadius: "0.25rem",
                    fontSize: "0.75rem",
                    fontWeight: 600,
                    backgroundColor: "#e0e7ff",
                    color: "#4338ca",
                    display: "flex",
                    alignItems: "center",
                    gap: "0.25rem",
                  }}
                >
                  <Database size={12} /> Graph: {c.graph_case_id}
                </span>
              )}
            </div>
            <p style={{ margin: "0.5rem 0 0 0", color: "#475569", fontSize: "0.95rem" }}>
              {c.summary}
            </p>
          </div>

          <div style={{ textAlign: "right" }}>
            <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Exposure</span>
            <div style={{ fontSize: "1.5rem", fontWeight: 700, color: isFraud ? "#b91c1c" : "#10b981" }}>
              ${c.exposure_usd.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </div>
            <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
              {data.tool_calls} Tool Calls • {data.tokens} Tokens • {data.latency_s}s
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: 2 Columns */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
        {/* Left Column: Evidence & Graph Analysis */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Pattern Card */}
          <div style={{ background: "white", padding: "1.25rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 0.75rem 0", fontSize: "1rem", fontWeight: 600, color: "#1e293b", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Fingerprint size={18} color="#6366f1" /> Fraud Pattern Analysis
            </h3>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <span style={{ fontWeight: 600, color: "#475569" }}>Typology:</span>
              <span style={{ padding: "0.2rem 0.5rem", borderRadius: "0.25rem", backgroundColor: "#f8fafc", border: "1px solid #cbd5e1", fontWeight: 700, color: "#0f172a" }}>
                {c.pattern}
              </span>
            </div>
            {c.pattern_description && (
              <div style={{ padding: "0.75rem", backgroundColor: "#fef3c7", borderRadius: "0.375rem", fontSize: "0.85rem", color: "#92400e", marginBottom: "0.5rem" }}>
                <strong>Undocumented Typology:</strong> {c.pattern_description}
              </div>
            )}
            {c.affected_txn_ids.length > 0 && (
              <div style={{ fontSize: "0.85rem", color: "#334155", marginTop: "0.5rem" }}>
                <strong>Affected Transactions ({c.affected_txn_ids.length}):</strong>{" "}
                {c.affected_txn_ids.join(", ")}
              </div>
            )}
            {c.connected_card_ids.length > 0 && (
              <div style={{ fontSize: "0.85rem", color: "#334155", marginTop: "0.25rem" }}>
                <strong>Connected Cards:</strong> {c.connected_card_ids.join(", ")}
              </div>
            )}
            {c.connected_device_profiles.length > 0 && (
              <div style={{ fontSize: "0.85rem", color: "#334155", marginTop: "0.25rem" }}>
                <strong>Device Profile:</strong> {c.connected_device_profiles[0]}
              </div>
            )}
            {c.similar_prior_cases.length > 0 && (
              <div style={{ fontSize: "0.85rem", color: "#4338ca", marginTop: "0.25rem" }}>
                <strong>Similar Past Cases (Graph Memory):</strong> {c.similar_prior_cases.join(", ")}
              </div>
            )}
          </div>

          {/* Evidence List */}
          <div style={{ background: "white", padding: "1.25rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 0.75rem 0", fontSize: "1rem", fontWeight: 600, color: "#1e293b", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <FileSearch size={18} color="#6366f1" /> Structured Graph & Verification Evidence
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {c.evidence.map((ev, i) => (
                <div key={i} style={{ padding: "0.75rem", backgroundColor: "#f8fafc", borderRadius: "0.5rem", border: "1px solid #e2e8f0" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#64748b", marginBottom: "0.25rem" }}>
                    <span style={{ textTransform: "uppercase", fontWeight: 700, color: ev.source === "customer" ? "#10b981" : "#6366f1" }}>
                      Source: {ev.source}
                    </span>
                    <span style={{ fontFamily: "monospace" }}>{ev.ref}</span>
                  </div>
                  <div style={{ fontSize: "0.875rem", color: "#1e293b", lineHeight: 1.4 }}>
                    {ev.claim}
                  </div>
                  {ev.entity_ids.length > 0 && (
                    <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "0.25rem" }}>
                      Entities: {ev.entity_ids.join(", ")}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Policy Decisions & SAR Filing */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Next Best Actions Card */}
          <div style={{ background: "white", padding: "1.25rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0" }}>
            <h3 style={{ margin: "0 0 0.75rem 0", fontSize: "1rem", fontWeight: 600, color: "#1e293b", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Shield size={18} color="#6366f1" /> Fraud Policy: Next Best Actions
            </h3>

            {/* Initial Actions */}
            <div style={{ marginBottom: "1rem" }}>
              <div style={{ fontSize: "0.8rem", textTransform: "uppercase", fontWeight: 700, color: "#64748b", marginBottom: "0.35rem" }}>
                1. Initial Recommendations (Pre-Evidence)
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                {next_best_actions.initial.map((act, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.5rem 0.75rem", backgroundColor: "#f8fafc", borderRadius: "0.375rem", border: "1px solid #e2e8f0" }}>
                    <div>
                      <strong style={{ color: "#0f172a", fontSize: "0.85rem" }}>{act.action}</strong>
                      <div style={{ fontSize: "0.75rem", color: "#64748b" }}>{act.reason}</div>
                    </div>
                    <span style={{ fontSize: "0.7rem", fontWeight: 700, padding: "0.15rem 0.4rem", borderRadius: "0.25rem", backgroundColor: act.route === "auto" ? "#e0e7ff" : "#fee2e2", color: act.route === "auto" ? "#4338ca" : "#b91c1c" }}>
                      {act.route}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Evidence Simulation */}
            {evidence_requests.length > 0 && (
              <div style={{ padding: "0.75rem", backgroundColor: "#eff6ff", borderRadius: "0.5rem", border: "1px solid #bfdbfe", marginBottom: "1rem" }}>
                <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#1e40af", marginBottom: "0.25rem" }}>
                  EVIDENCE SIMULATION ({evidence_requests[0].type})
                </div>
                <div style={{ fontSize: "0.85rem", color: "#1e3a8a", fontStyle: "italic" }}>
                  "{evidence_requests[0].assumed_response}"
                </div>
              </div>
            )}

            {/* Final Actions */}
            <div style={{ marginBottom: "0.75rem" }}>
              <div style={{ fontSize: "0.8rem", textTransform: "uppercase", fontWeight: 700, color: "#10b981", marginBottom: "0.35rem" }}>
                2. Final Recommendations (Post-Evidence)
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                {next_best_actions.final.map((act, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.5rem 0.75rem", backgroundColor: "#f0fdf4", borderRadius: "0.375rem", border: "1px solid #bbf7d0" }}>
                    <div>
                      <strong style={{ color: "#166534", fontSize: "0.85rem" }}>{act.action}</strong>
                      <div style={{ fontSize: "0.75rem", color: "#15803d" }}>{act.reason}</div>
                    </div>
                    <span style={{ fontSize: "0.7rem", fontWeight: 700, padding: "0.15rem 0.4rem", borderRadius: "0.25rem", backgroundColor: act.route === "auto" ? "#dcfce7" : "#fef3c7", color: act.route === "auto" ? "#166534" : "#b45309" }}>
                      {act.route}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ fontSize: "0.8rem", color: "#64748b", borderTop: "1px solid #f1f5f9", paddingTop: "0.5rem" }}>
              <strong>What Changed:</strong> {next_best_actions.what_changed}
            </div>
          </div>

          {/* SAR Regulatory Filing Card */}
          <div style={{ background: "white", padding: "1.25rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
              <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 600, color: "#1e293b", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <FileCheck size={18} color={sar.file ? "#f59e0b" : "#94a3b8"} /> FinCEN Suspicious Activity Report (SAR)
              </h3>
              {sar.file && (
                <button
                  onClick={handleCopyNarrative}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.25rem",
                    padding: "0.3rem 0.6rem",
                    borderRadius: "0.375rem",
                    border: "1px solid #cbd5e1",
                    background: "white",
                    cursor: "pointer",
                    fontSize: "0.75rem",
                    color: "#334155",
                  }}
                >
                  <Copy size={12} /> {copied ? "Copied!" : "Copy Narrative"}
                </button>
              )}
            </div>

            {sar.file ? (
              <div>
                <div style={{ display: "flex", gap: "1rem", fontSize: "0.8rem", color: "#64748b", marginBottom: "0.75rem" }}>
                  <span><strong>Total:</strong> ${sar.total_amount_usd.toFixed(2)}</span>
                  <span><strong>Dates:</strong> {sar.activity_dates.join(" to ")}</span>
                  <span><strong>Subjects:</strong> {sar.subjects.length} entities</span>
                </div>
                <div style={{ fontSize: "0.85rem", color: "#334155", lineHeight: 1.5, backgroundColor: "#fffbeb", padding: "0.85rem", borderRadius: "0.5rem", border: "1px solid #fde68a" }}>
                  {sar.narrative}
                </div>
                <div style={{ fontSize: "0.75rem", color: "#92400e", marginTop: "0.5rem" }}>
                  <strong>Filing Reason:</strong> {sar.reason}
                </div>
              </div>
            ) : (
              <div style={{ padding: "1rem", backgroundColor: "#f8fafc", borderRadius: "0.5rem", color: "#64748b", fontSize: "0.85rem" }}>
                <CheckCircle2 size={16} color="#10b981" style={{ display: "inline", marginRight: "0.5rem" }} />
                No SAR required. {sar.reason}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
