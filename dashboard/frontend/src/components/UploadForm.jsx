import { useState } from "react";
import { uploadCsv } from "../utils/api.js";

export default function UploadForm({ onResults }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await uploadCsv(file);
      onResults(data.predictions);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <input
        type="file"
        accept=".csv"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <button type="submit" disabled={!file || loading}>
        {loading ? "Analyzing..." : "Analyze Flows"}
      </button>
      {error && <div className="error">{error}</div>}
    </form>
  );
}
