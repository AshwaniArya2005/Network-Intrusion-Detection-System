import { useMemo, useState } from "react";
import UploadForm from "./UploadForm.jsx";
import PredictionTable from "./PredictionTable.jsx";
import ExplanationView from "./ExplanationView.jsx";

export default function Dashboard() {
  const [predictions, setPredictions] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [view, setView] = useState("analyst");

  function handleResults(results) {
    setPredictions(results);
    setSelectedId(results[0]?.flow_id ?? null);
  }

  const selected = useMemo(
    () => predictions.find((p) => p.flow_id === selectedId) ?? null,
    [predictions, selectedId]
  );

  return (
    <div className="app">
      <h1>XAI Network IDS Dashboard</h1>
      <p className="subtitle">Upload network flow records to get predictions and explanations.</p>

      <div className="card">
        <UploadForm onResults={handleResults} />
      </div>

      <div className="card">
        <PredictionTable predictions={predictions} selectedId={selectedId} onSelect={setSelectedId} />
      </div>

      <div className="card">
        <div className="toggle-group">
          <button className={view === "analyst" ? "active" : ""} onClick={() => setView("analyst")}>
            Analyst View
          </button>
          <button className={view === "technical" ? "active" : ""} onClick={() => setView("technical")}>
            Technical View
          </button>
        </div>
        <ExplanationView prediction={selected} view={view} />
      </div>
    </div>
  );
}
