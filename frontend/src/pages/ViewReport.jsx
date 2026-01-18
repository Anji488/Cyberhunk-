// frontend/src/pages/ViewReport.jsx
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import Chart from "react-apexcharts";

const BACKEND = "http://localhost:8000";

export default function ViewReport() {
  const { id } = useParams();
  const [report, setReport] = useState(null);

  useEffect(() => {
    axios
      .get(`${BACKEND}/insights/reports/${id}/`, { withCredentials: true })
      .then((res) => setReport(res.data))
      .catch(console.error);
  }, [id]);

  if (!report) return <p className="text-gray-400 p-4">Loading report...</p>;

  const sentiment = report.sentiment?.distribution || {};
  const summary = report.summary || {};

  return (
    <div className="max-w-6xl mx-auto p-6 text-white">
      <h1 className="text-2xl font-bold mb-4">📑 Report</h1>

      <p className="text-gray-400 mb-1">
        Created: {new Date(report.created_at).toLocaleString()}
      </p>

      {/* Summary Cards */}
      <div className="grid md:grid-cols-4 gap-4 mt-6">
        <Stat label="Posts" value={summary.posts || report.insights?.filter(i => i.type === "post").length || 0} />
        <Stat label="Comments" value={summary.comments || report.insights?.filter(i => i.type === "comment").length || 0} />
        <Stat label="Toxicity" value={`${report.toxicity?.score || 0}%`} />
        <Stat label="Privacy Risk" value={`${report.privacy?.score || 0}%`} />
      </div>

      {/* CHART */}
      {Object.keys(sentiment).length > 0 && (
        <div className="bg-gray-900 p-4 rounded-xl mt-8">
          <h2 className="font-bold mb-2">Sentiment Distribution</h2>
          <Chart
            type="pie"
            series={Object.values(sentiment)}
            options={{
              labels: Object.keys(sentiment),
              theme: { mode: "dark" },
            }}
          />
        </div>
      )}

      {/* Recommendations */}
      {report.recommendations?.length > 0 && (
        <div className="mt-8 bg-gray-900 p-4 rounded-xl">
          <h2 className="font-bold mb-3">Recommendations</h2>
          <ul className="list-disc ml-5 text-gray-300">
            {report.recommendations.map((r, idx) => (
              <li key={idx}>{r.text || r}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

const Stat = ({ label, value }) => (
  <div className="bg-gray-800 p-4 rounded-lg">
    <p className="text-gray-400 text-sm">{label}</p>
    <p className="text-xl font-bold">{value}</p>
  </div>
);
