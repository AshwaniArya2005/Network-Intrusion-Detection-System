function badgeClass(pred, isUnknown) {
  if (isUnknown) return "badge unknown";
  return pred === "Normal" ? "badge normal" : "badge attack";
}

export default function PredictionTable({ predictions, selectedId, onSelect }) {
  if (!predictions.length) {
    return <p className="empty-state">Upload a flow CSV to see predictions.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Flow ID</th>
          <th>Prediction</th>
          <th>Confidence</th>
          <th>Top Reason</th>
        </tr>
      </thead>
      <tbody>
        {predictions.map((p) => (
          <tr
            key={p.flow_id}
            className={`selectable ${selectedId === p.flow_id ? "selected" : ""}`}
            onClick={() => onSelect(p.flow_id)}
          >
            <td>{p.flow_id}</td>
            <td>
              <span className={badgeClass(p.prediction, p.is_unknown)}>{p.prediction}</span>
            </td>
            <td>{(p.confidence * 100).toFixed(1)}%</td>
            <td>{p.shap_top_features[0]?.feature ?? "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
