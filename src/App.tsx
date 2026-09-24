import { useState } from "react";
import {
  Activity,
  AlertTriangle,
  Database,
  FileSearch,
  Network,
  ShieldAlert,
} from "lucide-react";

import GraphExplorer from "./components/GraphExplorer";

type Page = "investigate" | "graph";

export default function App() {
  const [currentPage, setCurrentPage] =
    useState<Page>("investigate");

  const [caseId] = useState("CASE-001");

  const handleInvestigate = () => {
    setCurrentPage("investigate");
  };

  const handleGraphExplorer = () => {
    console.log("GRAPH CLICKED");
    setCurrentPage("graph");
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <ShieldAlert size={22} />
          </div>

          <div>
            <strong>TigerGraphAI</strong>
            <span>Fraud Investigation</span>
          </div>
        </div>

        <div className="nav-label">INVESTIGATION</div>

        <button
          className={`nav-item ${
            currentPage === "investigate" ? "active" : ""
          }`}
          onClick={handleInvestigate}
        >
          <FileSearch size={18} />
          Investigate
        </button>

        <button
          className="nav-item"
          onClick={() => console.log("CASES CLICKED")}
        >
          <Database size={18} />
          Cases
        </button>

        <button
          className={`nav-item ${
            currentPage === "graph" ? "active" : ""
          }`}
          onClick={handleGraphExplorer}
        >
          <Network size={18} />
          Graph Explorer
        </button>

        <div className="nav-label second">SYSTEM</div>

        <button
          className="nav-item"
          onClick={() => console.log("SYSTEM STATUS CLICKED")}
        >
          <Activity size={18} />
          System Status
        </button>
      </aside>

      <main className="main-content">
        {currentPage === "graph" ? (
          <GraphExplorer caseId={caseId} />
        ) : (
          <section className="panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">
                  Investigation Console
                </span>

                <h1>Fraud Investigation</h1>

                <p>
                  Analyze suspicious transactions and investigate
                  connected entities.
                </p>
              </div>
            </div>

            <div className="investigation-card">
              <div className="investigation-icon">
                <FileSearch size={24} />
              </div>

              <div>
                <strong>Case {caseId}</strong>

                <p>
                  Investigation API is connected and ready.
                </p>

                <div className="status-row">
                  <span className="status-dot" />
                  Backend connected
                </div>
              </div>
            </div>

            <div className="info-item">
              <AlertTriangle size={18} />

              <div>
                <strong>Development environment</strong>

                <p>
                  Investigation and graph data are currently
                  backed by the local development graph client.
                </p>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}