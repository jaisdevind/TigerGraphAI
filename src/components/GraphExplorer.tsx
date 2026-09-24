import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CircleDot,
  CreditCard,
  Database,
  FileSearch,
  Monitor,
  User,
  Info,
} from "lucide-react";

import {
  getCaseGraph,
  getCaseList,
  type GraphNode,
  type GraphNodeType,
} from "../services/api";

interface GraphExplorerProps {
  caseId: string;
  onCaseChange?: (newCaseId: string) => void;
}

const nodeIcons: Record<GraphNodeType, typeof User> = {
  customer: User,
  card: CreditCard,
  transaction: FileSearch,
  device: Monitor,
  case: Database,
};

const nodeLabels: Record<GraphNodeType, string> = {
  customer: "Customer",
  card: "Card",
  transaction: "Transaction",
  device: "Device Profile",
  case: "Case",
};

export default function GraphExplorer({
  caseId,
  onCaseChange,
}: GraphExplorerProps) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<
    { source: string; target: string; relationship: string }[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [caseList, setCaseList] = useState<string[]>([]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    getCaseList()
      .then((cases) => setCaseList(cases.map((c) => c.case_id)))
      .catch(console.error);
  }, []);

  useEffect(() => {
    let active = true;

    async function loadGraph() {
      try {
        setLoading(true);
        setError("");
        setSelectedNode(null);

        const graph = await getCaseGraph(caseId);

        if (!active) {
          return;
        }

        setNodes(graph.nodes);
        setEdges(graph.edges);
        if (graph.nodes.length > 0) {
          setSelectedNode(graph.nodes[0]);
        }
      } catch (err) {
        if (!active) {
          return;
        }

        setError(
          err instanceof Error
            ? err.message
            : "Failed to load graph data.",
        );
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadGraph();

    return () => {
      active = false;
    };
  }, [caseId]);

  const nodeMap = useMemo(
    () => new Map(nodes.map((node) => [node.id, node])),
    [nodes],
  );

  return (
    <section className="panel graph-panel" style={{ padding: "1.5rem", maxWidth: "1280px", margin: "0 auto" }}>
      <div className="panel-heading" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <span className="eyebrow" style={{ fontSize: "0.85rem", color: "#6366f1", fontWeight: 600 }}>GRAPH EXPLORER</span>
          <h2 style={{ fontSize: "1.5rem", fontWeight: 700, margin: "0.25rem 0" }}>Investigation Relationship Subgraph</h2>
          <p style={{ color: "#64748b", margin: 0, fontSize: "0.9rem" }}>
            Visualizing entities, identity fingerprints, and multi-hop relationships for <strong>{caseId}</strong>.
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
          {caseList.length > 0 && onCaseChange && (
            <select
              value={caseId}
              onChange={(e) => onCaseChange(e.target.value)}
              style={{
                padding: "0.4rem 0.8rem",
                borderRadius: "0.375rem",
                border: "1px solid #cbd5e1",
                fontWeight: 600,
                color: "#1e293b",
                backgroundColor: "white",
              }}
            >
              {caseList.map((id) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
            </select>
          )}

          <div className="graph-summary" style={{ fontSize: "0.85rem", color: "#475569", background: "#f1f5f9", padding: "0.4rem 0.8rem", borderRadius: "0.375rem" }}>
            <span><strong>{nodes.length}</strong> nodes</span> • <span><strong>{edges.length}</strong> edges</span>
          </div>
        </div>
      </div>

      {loading ? (
        <div style={{ padding: "3rem", textAlign: "center", color: "#64748b" }}>
          Loading investigation subgraph...
        </div>
      ) : error ? (
        <div className="warning-item" style={{ padding: "1rem", backgroundColor: "#fef2f2", color: "#b91c1c", borderRadius: "0.5rem" }}>
          <AlertTriangle size={18} />
          <div>
            <strong>Graph unavailable:</strong> {error}
          </div>
        </div>
      ) : (
        <div className="graph-layout" style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "1.5rem" }}>
          {/* Visual Canvas of Nodes */}
          <div
            className="graph-canvas"
            style={{
              background: "#0f172a",
              borderRadius: "0.75rem",
              padding: "1.5rem",
              minHeight: "450px",
              display: "flex",
              flexWrap: "wrap",
              alignContent: "flex-start",
              gap: "1rem",
              boxShadow: "inset 0 2px 4px rgba(0,0,0,0.2)",
            }}
          >
            {nodes.map((node) => {
              const Icon = nodeIcons[node.type];
              const isSelected = selectedNode?.id === node.id;

              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`graph-node graph-node-${node.type}`}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.75rem",
                    padding: "0.75rem 1rem",
                    borderRadius: "0.5rem",
                    backgroundColor: isSelected ? "#3b82f6" : "#1e293b",
                    border: `1.5px solid ${isSelected ? "#60a5fa" : "#334155"}`,
                    color: "white",
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                  }}
                >
                  <div
                    style={{
                      background: isSelected ? "rgba(255,255,255,0.2)" : "#334155",
                      padding: "0.4rem",
                      borderRadius: "0.375rem",
                    }}
                  >
                    <Icon size={18} color="#f8fafc" />
                  </div>

                  <div>
                    <span style={{ fontSize: "0.7rem", textTransform: "uppercase", color: "#94a3b8", display: "block" }}>
                      {nodeLabels[node.type]}
                    </span>
                    <strong style={{ fontSize: "0.85rem", color: "#f8fafc" }}>{node.label}</strong>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Details & Relationships Panel */}
          <aside className="graph-details" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {/* Selected Node Details */}
            {selectedNode && (
              <div style={{ background: "white", padding: "1.25rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                  <Info size={16} color="#6366f1" />
                  <strong style={{ fontSize: "0.9rem", color: "#0f172a" }}>Node Inspector</strong>
                </div>
                <div style={{ fontSize: "0.85rem", color: "#475569" }}>
                  <div><strong>ID:</strong> {selectedNode.id}</div>
                  <div><strong>Type:</strong> {selectedNode.type}</div>
                  {Object.entries(selectedNode.metadata || {}).map(([k, v]) => (
                    <div key={k}>
                      <strong>{k}:</strong> {v}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Relationships list */}
            <div style={{ background: "white", padding: "1.25rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0", flex: 1 }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                <CircleDot size={16} color="#10b981" />
                <strong style={{ fontSize: "0.9rem", color: "#0f172a" }}>Graph Relationships</strong>
              </div>

              {edges.length === 0 ? (
                <p style={{ color: "#94a3b8", fontSize: "0.85rem" }}>No relationships in this subgraph.</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", maxHeight: "280px", overflowY: "auto" }}>
                  {edges.map((edge, index) => (
                    <div
                      key={`${edge.source}-${edge.target}-${index}`}
                      style={{
                        padding: "0.5rem",
                        backgroundColor: "#f8fafc",
                        borderRadius: "0.375rem",
                        border: "1px solid #e2e8f0",
                        fontSize: "0.75rem",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                      }}
                    >
                      <span style={{ fontWeight: 600, color: "#1e293b", maxWidth: "90px", overflow: "hidden", textOverflow: "ellipsis" }}>
                        {nodeMap.get(edge.source)?.label ?? edge.source}
                      </span>
                      <span style={{ padding: "0.15rem 0.4rem", backgroundColor: "#e0e7ff", color: "#4338ca", borderRadius: "0.25rem", fontWeight: 700 }}>
                        {edge.relationship}
                      </span>
                      <span style={{ fontWeight: 600, color: "#1e293b", maxWidth: "90px", overflow: "hidden", textOverflow: "ellipsis" }}>
                        {nodeMap.get(edge.target)?.label ?? edge.target}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </aside>
        </div>
      )}

      <div style={{ marginTop: "1.5rem", fontSize: "0.8rem", color: "#64748b", display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <AlertTriangle size={14} color="#f59e0b" />
        Graph data loaded via TigerGraphAI Graph Service & Knowledge Base.
      </div>
    </section>
  );
}
