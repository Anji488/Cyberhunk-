// frontend/src/components/ReportDetails.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

const BACKEND_URL = "http://localhost:8000/insights";

export default function ReportDetails({ reportId }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!reportId) return;
    setLoading(true);
    axios.get(`${BACKEND_URL}/reports/${reportId}/`)
      .then(res => {
        setReport(res.data.report);
      })
      .catch(err => {
        console.error("Failed to fetch report", err);
      })
      .finally(() => setLoading(false));
  }, [reportId]);

  if (!reportId) return <div>Select a report to view details.</div>;
  if (loading) return <div>Loading report...</div>;
  if (!report) return <div>Report not found.</div>;

  return (
    <div className="p-4 bg-gray-800 rounded text-gray-200">
      <h2 className="text-xl font-semibold mb-2">Report: {new Date(report.created_at).toLocaleString()}</h2>
      <div className="mb-3 text-sm text-gray-400">Status: {report.status} — Analysis time: {report.report_metadata?.analysis_time_seconds?.toFixed(1)}s</div>
      <div className="mb-3">
        <h3 className="font-semibold">Summary Metrics</h3>
        <pre className="bg-gray-900 p-2 rounded text-xs overflow-auto">{JSON.stringify(report.insightMetrics, null, 2)}</pre>
      </div>
      <div className="mb-3">
        <h3 className="font-semibold">Recommendations</h3>
        <ul className="list-disc ml-6">
          {(report.recommendations || []).map((r, i) => <li key={i}>{r}</li>)}
        </ul>
      </div>
      <div className="mb-3">
        <h3 className="font-semibold">Sample Insights (first 10 entries)</h3>
        <pre className="bg-gray-900 p-2 rounded text-xs overflow-auto">{JSON.stringify((report.insights || []).slice(0,10), null, 2)}</pre>
      </div>
    </div>
  );
}
