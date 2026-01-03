import React, { useEffect, useState } from "react";
import axios from "axios";
import Cookies from "js-cookie";

import AnalyzeToken from "../components/AnalyzeToken";

const BACKEND_URL = "https://cyberhunk.onrender.com";

export default function ReportsPage({ token }) {
  const [profile, setProfile] = useState(null);       
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  useEffect(() => {
    const fetchReports = async () => {
      if (!profile?.id) {
        setReports([]);
        setSelectedReport(null);
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        console.log("Fetching reports for profile:", profile.id);

        const res = await axios.get(`${BACKEND_URL}/insights/reports/`, {
          params: { profile_id: profile.id },
          withCredentials: true,
        });

        const list = res.data?.reports || [];
        setReports(list);

        if (list.length > 0) {
          sorted.sort(
            (a, b) => new Date(b.created_at) - new Date(a.created_at)
          );

          fetchReport(sorted[0].report_id);
        } else {
          setSelectedReport(null);
        }
      } catch (err) {
        console.error("Error fetching reports:", err);
        setError("Failed to load reports.");
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [profile?.id]);

  // -----------------------------
  // Fetch single report
  // -----------------------------
  const fetchReport = async (reportId) => {
    if (!reportId) return;

    setLoading(true);
    setError(null);

    try {
      const res = await axios.get(`${BACKEND_URL}/insights/reports/${reportId}/`, {
        withCredentials: true,
      });
      setSelectedReport(res.data || null);
    } catch (err) {
      console.error("Error fetching report:", err);
      setError("Unable to load report.");
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------
  // Render
  // -----------------------------
  return (
    <div>
      {/* Step 1: Load Profile using AnalyzeToken */}
      {!profile && (
        <AnalyzeToken
          token={token}
          onInsightsFetched={(data) => setProfile(data.profile)}
        />
      )}

      {/* Step 2: Reports */}
      {loading && <p className="p-4 text-gray-400">Loading reports...</p>}
      {error && <p className="p-4 text-red-500 font-semibold">{error}</p>}
      {!loading && !error && !reports.length && profile && (
        <p className="p-4 text-gray-400">No reports found for this profile.</p>
      )}

      {!loading && !error && reports.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Past Reports</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {reports.map((r) => (
              <div
                key={r.report_id}
                className={`p-4 border rounded-lg cursor-pointer hover:bg-gray-800 ${
                  selectedReport?.report_id === r.report_id ? "bg-gray-800" : "bg-gray-900"
                }`}
                onClick={() => fetchReport(r.report_id)}
              >
                <p className="font-semibold">Report ID: {r.report_id}</p>
                <p className="text-sm text-gray-400">
                  Created: {new Date(r.created_at).toLocaleString()}
                </p>
                <p className="text-sm text-gray-400">Status: {r.status || "Completed"}</p>
              </div>
            ))}
          </div>

          {selectedReport && (
            <div className="bg-gray-900 p-6 rounded-lg border border-gray-700">
              <h2 className="text-xl font-bold mb-4">Report Details</h2>

              {selectedReport.profile && (
                <div className="flex items-center mb-6">
                  <img
                    src={selectedReport.profile.picture?.data?.url}
                    className="w-16 h-16 rounded-full mr-4"
                    alt="Profile"
                  />
                  <div>
                    <p className="text-lg font-semibold">{selectedReport.profile.name}</p>
                    <p className="text-sm text-gray-400">
                      Birthday: {selectedReport.profile.birthday || "N/A"}
                    </p>
                    <p className="text-sm text-gray-400">
                      Gender: {selectedReport.profile.gender || "N/A"}
                    </p>
                  </div>
                </div>
              )}

              {selectedReport.insightMetrics?.length > 0 && (
                <>
                  <h3 className="font-semibold">Insight Metrics</h3>
                  <ul className="list-disc ml-6 mb-4">
                    {selectedReport.insightMetrics.map((m, i) => (
                      <li key={i}>{m.title}: {m.value}%</li>
                    ))}
                  </ul>
                </>
              )}

              {selectedReport.recommendations?.length > 0 && (
                <>
                  <h3 className="font-semibold">Recommendations</h3>
                  <ul className="list-disc ml-6">
                    {selectedReport.recommendations.map((r, i) => (
                      <li key={i}>{r.text}</li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
