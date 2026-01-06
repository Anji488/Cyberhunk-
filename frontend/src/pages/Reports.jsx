import React, { useEffect, useState } from "react";
import axios from "axios";
import AnalyzeToken from "../components/AnalyzeToken";

const BACKEND_URL = "https://cyberhunk.onrender.com";

export default function ReportsPage({ token }) {
  const [profile, setProfile] = useState(null);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!profile?.id) return;

    setLoading(true);

    axios.get(`${BACKEND_URL}/insights/reports/`, {
      params: { profile_id: profile.id },
      withCredentials: true,
    })
    .then(res => {
      setReports(res.data?.reports || []);
    })
    .finally(() => setLoading(false));

  }, [profile?.id]);

  return (
    <div className="p-6 text-white">

      {/* STEP 1: LOAD PROFILE */}
      {!profile && (
        <AnalyzeToken
          token={token}
          onProfileLoaded={setProfile}
        />
      )}

      {/* STEP 2: REPORTS TABLE */}
      {profile && (
        <>
          <h1 className="text-2xl font-bold mb-4">📊 Reports</h1>

          {loading && <p className="text-gray-400">Loading reports…</p>}

          {!loading && reports.length === 0 && (
            <p className="text-gray-400">No reports found.</p>
          )}

          {reports.length > 0 && (
            <table className="w-full border border-gray-700 rounded-lg overflow-hidden">
              <thead className="bg-gray-800">
                <tr>
                  <th className="p-3 text-left">Created</th>
                  <th className="p-3 text-left">Status</th>
                  <th className="p-3 text-left">Action</th>
                </tr>
              </thead>
              <tbody>
                {reports.map(r => (
                  <tr key={r.report_id} className="border-t border-gray-700">
                    <td className="p-3">
                      {new Date(r.created_at).toLocaleString()}
                    </td>
                    <td className="p-3">{r.status}</td>
                    <td className="p-3">
                      <a
                        href={`/reports/${r.report_id}`}
                        className="text-indigo-400 hover:underline"
                      >
                        View Report
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </div>
  );
}
