import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = "https://cyberhunk.onrender.com";

export default function ViewReport() {
  const { id } = useParams();
  const [report, setReport] = useState(null);

  useEffect(() => {
    axios.get(`${BACKEND_URL}/insights/reports/${id}/`, {
      withCredentials: true
    })
    .then(res => setReport(res.data))
    .catch(() => setReport(null));
  }, [id]);

  if (!report) {
    return <p className="p-6 text-gray-400">Loading report…</p>;
  }

  return (
    <div className="max-w-5xl mx-auto p-6 text-white">

      <h1 className="text-2xl font-bold mb-2">📑 Report</h1>
      <p className="text-gray-400 mb-6">
        Created: {new Date(report.created_at).toLocaleString()}
      </p>

      {/* PROFILE */}
      {report.profile && (
        <div className="flex items-center mb-6">
          <img
            src={report.profile.picture?.data?.url}
            className="w-16 h-16 rounded-full mr-4"
            alt="Profile"
          />
          <div>
            <p className="font-semibold text-lg">{report.profile.name}</p>
            <p className="text-gray-400 text-sm">
              {report.profile.gender || "N/A"}
            </p>
          </div>
        </div>
      )}

      {/* METRICS */}
      <section className="mb-6">
        <h2 className="font-semibold mb-2">Insight Metrics</h2>
        <ul className="list-disc ml-6 text-gray-300">
          {report.insightMetrics?.map((m, i) => (
            <li key={i}>{m.title}: {m.value}%</li>
          ))}
        </ul>
      </section>

      {/* RECOMMENDATIONS */}
      <section>
        <h2 className="font-semibold mb-2">Recommendations</h2>
        <ul className="list-disc ml-6 text-gray-300">
          {report.recommendations?.map((r, i) => (
            <li key={i}>{r.text}</li>
          ))}
        </ul>
      </section>

    </div>
  );
}
