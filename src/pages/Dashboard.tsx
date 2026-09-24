import { useEffect, useState } from "react";
import {
  AlertOctagon,
  CheckCircle2,
  FileCheck,
  FileSearch,
  Network,
  RefreshCw,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";
import { getCaseList, generateAllCases } from "../services/api";
import type { CaseSummaryItem } from "../types/case";

interface DashboardProps {
  onSelectCase: (caseId: string, page: "investigate" | "graph") => void;
}

export default function Dashboard({ onSelectCase }: DashboardProps) {
  const [cases, setCases] = useState<CaseSummaryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "fraud" | "legitimate" | "sar">("all");
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await getCaseList();
      setCases(data);
    } catch (err) {
      console.error("Failed to load cases", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleGenerateAll = async () => {
    try {
      setIsGenerating(true);
      setStatusMsg("Running agentic investigation across all 20 benchmark cases...");
      await generateAllCases();
      setStatusMsg("Batch completed! 20 cases written to cases/ and persisted to graph.");
      await loadData();
    } catch (err) {
      setStatusMsg("Batch generation failed.");
    } finally {
      setIsGenerating(false);
      setTimeout(() => setStatusMsg(""), 5000);
    }
  };

  const fraudCount = cases.filter((c) => c.verdict === "fraud").length;
  const legitimateCount = cases.filter((c) => c.verdict === "legitimate").length;
  const sarCount = cases.filter((c) => c.sar_filed).length;
  const totalExposure = cases.reduce((acc, c) => acc + (c.exposure_usd || 0), 0);

  const filteredCases = cases.filter((c) => {
    if (filter === "fraud") return c.verdict === "fraud";
    if (filter === "legitimate") return c.verdict === "legitimate";
    if (filter === "sar") return c.sar_filed;
    return true;
  });

  return (
    <div className="dashboard-container" style={{ padding: "1.5rem", maxWidth: "1280px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <span style={{ fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#6366f1", fontWeight: 600 }}>
            TigerGraph × Hacker House Goa
          </span>
          <h1 style={{ fontSize: "1.875rem", fontWeight: 700, margin: "0.25rem 0", color: "#0f172a" }}>
            Fraud Investigation Command Center
          </h1>
          <p style={{ color: "#64748b", margin: 0, fontSize: "0.95rem" }}>
            Autonomous multi-agent investigation, FinCEN regulatory filing & graph case memory for the 20 benchmark cases.
          </p>
        </div>

        <button
          onClick={handleGenerateAll}
          disabled={isGenerating}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
            backgroundColor: "#4f46e5",
            color: "white",
            padding: "0.6rem 1.2rem",
            borderRadius: "0.5rem",
            border: "none",
            fontWeight: 600,
            cursor: isGenerating ? "not-allowed" : "pointer",
            boxShadow: "0 2px 4px rgba(79, 70, 229, 0.2)",
          }}
        >
          <RefreshCw size={16} className={isGenerating ? "animate-spin" : ""} />
          {isGenerating ? "Investigating..." : "Re-run 20 Cases Batch"}
        </button>
      </div>

      {statusMsg && (
        <div style={{ padding: "0.75rem 1rem", backgroundColor: "#e0e7ff", color: "#3730a3", borderRadius: "0.375rem", marginBottom: "1.5rem", fontWeight: 500 }}>
          {statusMsg}
        </div>
      )}

      {/* Metrics Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        <div style={{ background: "white", padding: "1.25rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "0.875rem", fontWeight: 500 }}>
            <span>Total Exam Cases</span>
            <FileSearch size={18} color="#6366f1" />
          </div>
          <div style={{ fontSize: "1.75rem", fontWeight: 700, color: "#0f172a", marginTop: "0.5rem" }}>
            {cases.length}
          </div>
          <div style={{ fontSize: "0.8rem", color: "#10b981", marginTop: "0.25rem" }}>100% Processed</div>
        </div>

        <div style={{ background: "white", padding: "1.25rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "0.875rem", fontWeight: 500 }}>
            <span>Confirmed Fraud</span>
            <AlertOctagon size={18} color="#ef4444" />
          </div>
          <div style={{ fontSize: "1.75rem", fontWeight: 700, color: "#ef4444", marginTop: "0.5rem" }}>
            {fraudCount}
          </div>
          <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.25rem" }}>Testing, CNP, ATO, Rings</div>
        </div>

        <div style={{ background: "white", padding: "1.25rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "0.875rem", fontWeight: 500 }}>
            <span>Cleared False Alarms</span>
            <CheckCircle2 size={18} color="#10b981" />
          </div>
          <div style={{ fontSize: "1.75rem", fontWeight: 700, color: "#10b981", marginTop: "0.5rem" }}>
            {legitimateCount}
          </div>
          <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.25rem" }}>Travel, Recurring, Verified</div>
        </div>

        <div style={{ background: "white", padding: "1.25rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "0.875rem", fontWeight: 500 }}>
            <span>Regulatory SARs Filed</span>
            <FileCheck size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: "1.75rem", fontWeight: 700, color: "#f59e0b", marginTop: "0.5rem" }}>
            {sarCount}
          </div>
          <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.25rem" }}>FinCEN Section 3a Standard</div>
        </div>

        <div style={{ background: "white", padding: "1.25rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "#64748b", fontSize: "0.875rem", fontWeight: 500 }}>
            <span>Identified Exposure</span>
            <TrendingUp size={18} color="#8b5cf6" />
          </div>
          <div style={{ fontSize: "1.75rem", fontWeight: 700, color: "#8b5cf6", marginTop: "0.5rem" }}>
            ${totalExposure.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.25rem" }}>USD in Fraud Episodes</div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem", borderBottom: "1px solid #e2e8f0", paddingBottom: "0.5rem" }}>
        {[
          { key: "all", label: "All 20 Cases" },
          { key: "fraud", label: `Confirmed Fraud (${fraudCount})` },
          { key: "legitimate", label: `Legitimate Activity (${legitimateCount})` },
          { key: "sar", label: `SARs Required (${sarCount})` },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key as any)}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "0.375rem",
              border: "none",
              backgroundColor: filter === tab.key ? "#e0e7ff" : "transparent",
              color: filter === tab.key ? "#4338ca" : "#64748b",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Cases Table */}
      <div style={{ background: "white", borderRadius: "0.75rem", border: "1px solid #e2e8f0", overflow: "hidden", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
        {loading ? (
          <div style={{ padding: "3rem", textAlign: "center", color: "#64748b" }}>Loading cases...</div>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "0.9rem" }}>
            <thead>
              <tr style={{ backgroundColor: "#f8fafc", borderBottom: "1px solid #e2e8f0", color: "#475569", fontWeight: 600 }}>
                <th style={{ padding: "0.85rem 1rem" }}>Case ID</th>
                <th style={{ padding: "0.85rem 1rem" }}>Customer & Card</th>
                <th style={{ padding: "0.85rem 1rem" }}>Trigger / Txn</th>
                <th style={{ padding: "0.85rem 1rem" }}>Verdict</th>
                <th style={{ padding: "0.85rem 1rem" }}>Pattern</th>
                <th style={{ padding: "0.85rem 1rem" }}>Exposure</th>
                <th style={{ padding: "0.85rem 1rem" }}>SAR</th>
                <th style={{ padding: "0.85rem 1rem", textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredCases.map((c) => {
                const isFraud = c.verdict === "fraud";
                return (
                  <tr key={c.case_id} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "0.85rem 1rem", fontWeight: 700, color: "#1e293b" }}>
                      {c.case_id}
                    </td>
                    <td style={{ padding: "0.85rem 1rem" }}>
                      <div style={{ fontWeight: 600, color: "#334155" }}>{c.customer_id}</div>
                      <div style={{ fontSize: "0.8rem", color: "#64748b" }}>{c.card_id}</div>
                    </td>
                    <td style={{ padding: "0.85rem 1rem" }}>
                      <span style={{ fontSize: "0.75rem", padding: "0.2rem 0.5rem", borderRadius: "0.25rem", backgroundColor: "#f1f5f9", color: "#475569", fontWeight: 500 }}>
                        {c.trigger_type}
                      </span>
                      <div style={{ fontSize: "0.8rem", color: "#64748b", marginTop: "0.2rem" }}>
                        Txn: {c.flagged_txn_id}
                      </div>
                    </td>
                    <td style={{ padding: "0.85rem 1rem" }}>
                      <span
                        style={{
                          padding: "0.25rem 0.65rem",
                          borderRadius: "9999px",
                          fontSize: "0.75rem",
                          fontWeight: 700,
                          backgroundColor: isFraud ? "#fee2e2" : "#dcfce7",
                          color: isFraud ? "#b91c1c" : "#15803d",
                        }}
                      >
                        {c.verdict.toUpperCase()} ({(c.fraud_probability * 100).toFixed(0)}%)
                      </span>
                    </td>
                    <td style={{ padding: "0.85rem 1rem" }}>
                      <span style={{ color: "#334155", fontWeight: 500 }}>
                        {c.pattern === "none" ? "—" : c.pattern.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td style={{ padding: "0.85rem 1rem", fontWeight: 600, color: isFraud ? "#b91c1c" : "#64748b" }}>
                      {c.exposure_usd > 0 ? `$${c.exposure_usd.toFixed(2)}` : "—"}
                    </td>
                    <td style={{ padding: "0.85rem 1rem" }}>
                      {c.sar_filed ? (
                        <span style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem", padding: "0.2rem 0.5rem", backgroundColor: "#fef3c7", color: "#b45309", borderRadius: "0.25rem", fontSize: "0.75rem", fontWeight: 700 }}>
                          <ShieldAlert size={12} /> FILED
                        </span>
                      ) : (
                        <span style={{ color: "#94a3b8", fontSize: "0.8rem" }}>None</span>
                      )}
                    </td>
                    <td style={{ padding: "0.85rem 1rem", textAlign: "right" }}>
                      <div style={{ display: "inline-flex", gap: "0.5rem" }}>
                        <button
                          onClick={() => onSelectCase(c.case_id, "investigate")}
                          title="View Case Investigation"
                          style={{
                            padding: "0.4rem 0.6rem",
                            borderRadius: "0.375rem",
                            border: "1px solid #cbd5e1",
                            background: "white",
                            color: "#334155",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            gap: "0.25rem",
                            fontSize: "0.8rem",
                            fontWeight: 600,
                          }}
                        >
                          <FileSearch size={14} /> Review
                        </button>
                        <button
                          onClick={() => onSelectCase(c.case_id, "graph")}
                          title="Explore Case Subgraph"
                          style={{
                            padding: "0.4rem 0.6rem",
                            borderRadius: "0.375rem",
                            border: "1px solid #6366f1",
                            background: "#eff6ff",
                            color: "#4f46e5",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            gap: "0.25rem",
                            fontSize: "0.8rem",
                            fontWeight: 600,
                          }}
                        >
                          <Network size={14} /> Graph
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
