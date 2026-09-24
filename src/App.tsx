import { useState } from "react";
import {
  FileSearch,
  LayoutDashboard,
  Network,
  ShieldAlert,
} from "lucide-react";

import Dashboard from "./pages/Dashboard";
import CaseInvestigation from "./pages/CaseInvestigation";
import GraphExplorer from "./components/GraphExplorer";

type Page = "dashboard" | "investigate" | "graph";

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");
  const [selectedCaseId, setSelectedCaseId] = useState<string>("HHG-001");

  const handleSelectCaseFromDashboard = (caseId: string, targetPage: "investigate" | "graph") => {
    setSelectedCaseId(caseId);
    setCurrentPage(targetPage);
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand" onClick={() => setCurrentPage("dashboard")} style={{ cursor: "pointer" }}>
          <div className="brand-icon">
            <ShieldAlert size={22} />
          </div>

          <div>
            <strong>TigerGraphAI</strong>
            <span>Fraud Agent</span>
          </div>
        </div>

        <div className="nav-label">COMMAND CENTER</div>

        <button
          className={`nav-item ${currentPage === "dashboard" ? "active" : ""}`}
          onClick={() => setCurrentPage("dashboard")}
        >
          <LayoutDashboard size={18} />
          Dashboard
        </button>

        <button
          className={`nav-item ${currentPage === "investigate" ? "active" : ""}`}
          onClick={() => setCurrentPage("investigate")}
        >
          <FileSearch size={18} />
          Investigation Console
        </button>

        <button
          className={`nav-item ${currentPage === "graph" ? "active" : ""}`}
          onClick={() => setCurrentPage("graph")}
        >
          <Network size={18} />
          Graph Explorer
        </button>

        <div className="nav-label second">SUBMISSION</div>

        <div style={{ padding: "0.5rem 1rem", fontSize: "0.8rem", color: "#94a3b8" }}>
          <div><strong>Case Pack:</strong> 20 / 20</div>
          <div><strong>Folder:</strong> cases/</div>
          <div style={{ marginTop: "0.25rem", color: "#10b981", fontWeight: 600 }}>✓ All Validated</div>
        </div>
      </aside>

      <main className="main-content" style={{ overflowY: "auto", height: "100vh", backgroundColor: "#f8fafc" }}>
        {currentPage === "dashboard" && (
          <Dashboard onSelectCase={handleSelectCaseFromDashboard} />
        )}

        {currentPage === "investigate" && (
          <CaseInvestigation
            currentCaseId={selectedCaseId}
            onCaseChange={setSelectedCaseId}
            onOpenGraph={(cId) => {
              setSelectedCaseId(cId);
              setCurrentPage("graph");
            }}
          />
        )}

        {currentPage === "graph" && (
          <GraphExplorer
            caseId={selectedCaseId}
            onCaseChange={setSelectedCaseId}
          />
        )}
      </main>
    </div>
  );
}
