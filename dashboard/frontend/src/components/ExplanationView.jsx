export default function ExplanationView({ prediction, view }) {
  if (!prediction) {
    return <p className="empty-state">Select a flow from the table to see its explanation.</p>;
  }

  if (view === "analyst") {
    return <p className="narrative">{prediction.narrative}</p>;
  }

  const maxAbs = Math.max(...prediction.shap_top_features.map((f) => Math.abs(f.value)), 1e-9);

  return (
    <div>
      {prediction.shap_top_features.map((f) => {
        const pct = (Math.abs(f.value) / maxAbs) * 100;
        const positive = f.value >= 0;
        return (
          <div className="shap-bar-row" key={f.feature}>
            <span>{f.feature}</span>
            <div className="shap-bar-track">
              <div
                className={`shap-bar-fill ${positive ? "positive" : "negative"}`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span>{f.value.toFixed(3)}</span>
          </div>
        );
      })}
    </div>
  );
}
