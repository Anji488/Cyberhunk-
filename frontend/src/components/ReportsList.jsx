// frontend/src/components/ReportsList.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import Cookies from "js-cookie";

const BACKEND_URL = "https://cyberhunk.onrender.com/insights";

export default function ReportsList({ onSelectReport }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const token = Cookies.get("fb_token") || null;

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    setLoading(true);
    axios.get(`${BACKEND_URL}/reports/`, { params: { token }})
      .then(res => {
        setReports(res.data.reports || []);
      })
      .catch(err => {
        console.error("Failed to fetch reports", err);
      })
      .finally(() => setLoading(false));
  }, [token]);

  if (!token) return <p className="text-yellow-400">Please login to view reports.</p>;
  if (loading) return <p>Loading reports...</p>;
  if (!reports.length) return <p>No reports yet. Generate one from the Analyze page.</p>;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Report History</h3>
      <ul>
        {reports.map(r => (
          <li key={r._id} className="p-3 border rounded mb-2 flex justify-between items-center">
            <div>
              <div className="font-medium">{new Date(r.created_at).toLocaleString()}</div>
              <div className="text-sm text-gray-400">Status: {r.status} — Posts: {r.report_metadata?.post_count || 0} Comments: {r.report_metadata?.comment_count || 0}</div>
            </div>
            <div className="flex gap-2">
              <button onClick={() => onSelectReport(r._id)} className="px-3 py-1 bg-indigo-600 rounded text-white">View</button>
              <button onClick={async () => {
                try {
                  // regenerate: create a new report based on current token
                  const res = await axios.post(`${BACKEND_URL}/reports/${r._id}/regenerate/`, null, { params: { token }});
                  // optionally refresh list afterwards
                  window.location.reload();
                } catch (err) {
                  console.error("Regenerate failed", err);
                }
              }} className="px-3 py-1 bg-gray-700 rounded text-white">Regenerate</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
