// frontend/src/pages/Reports.jsx
import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import AnalyzeToken from "../components/AnalyzeToken";
import html2canvas from "html2canvas";

const BACKEND_URL = "https://cyberhunk.onrender.com";

export default function ReportsPage({ token }) {
  const [profile, setProfile] = useState(null);
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const reportRef = useRef(null);

  
  // Fetch reports when profile.id exists
  
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
        const res = await axios.get(`${BACKEND_URL}/insights/reports/`, {
          params: { profile_id: String(profile.id) },
          withCredentials: true,
        });

        const list = res.data?.reports || [];

        if (list.length > 0) {
          const sorted = list.sort(
            (a, b) => new Date(b.created_at) - new Date(a.created_at)
          );
          setReports(sorted);
        } else {
          setReports([]);
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

  
  // Fetch single report by report_id
  
  const fetchReport = async (reportId) => {
    if (!reportId) return;

    setLoading(true);
    setError(null);

    try {
      const res = await axios.get(`${BACKEND_URL}/insights/reports/${reportId}/`, {
        withCredentials: true,
      });
      setSelectedReport(res.data || null);
      setIsModalOpen(true); // open modal automatically
    } catch (err) {
      console.error("Error fetching report:", err);
      setError("Unable to load report.");
    } finally {
      setLoading(false);
    }
  };

  
  // Download report as PNG
  
  const downloadReportAsPNG = async () => {
    if (!reportRef.current) return;
    const canvas = await html2canvas(reportRef.current, { scale: 2 });
    const link = document.createElement("a");
    link.download = `report_${selectedReport.report_id}.png`;
    link.href = canvas.toDataURL("image/png");
    link.click();
  };

  
  // Render
  
  return (
    <div className="max-w-6xl mx-auto p-6 text-gray-800 bg-gray-50 min-h-screen">
      {/* Step 1: Load Profile */}
      {!profile && (
        <AnalyzeToken
          token={token}
          onInsightsFetched={(data) => setProfile(data.profile)}
        />
      )}

      {/* Step 2: Reports Table */}
      {loading && <p className="p-4 text-gray-500">Loading reports...</p>}
      {error && <p className="p-4 text-red-600 font-semibold">{error}</p>}
      {!loading && !error && profile && reports.length === 0 && (
        <p className="p-4 text-gray-500">No reports found for this profile.</p>
      )}

      {!loading && !error && reports.length > 0 && (
        <div className="mt-6">
          <h2 className="text-2xl font-bold mb-4">Past Reports</h2>

          <div className="overflow-x-auto">
            <table className="min-w-full bg-white shadow-md rounded-lg">
              <thead className="bg-gray-200">
                <tr>
                  <th className="py-3 px-6 text-left font-medium">Report ID</th>
                  <th className="py-3 px-6 text-left font-medium">Created</th>
                  <th className="py-3 px-6 text-left font-medium">Status</th>
                  <th className="py-3 px-6 text-center font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r) => (
                  <tr
                    key={r.report_id}
                    className="border-b hover:bg-gray-100 transition"
                  >
                    <td className="py-3 px-6">{r.report_id}</td>
                    <td className="py-3 px-6">
                      {new Date(r.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-6">{r.status || "Completed"}</td>
                    <td className="py-3 px-6 text-center">
                      <button
                        onClick={() => fetchReport(r.report_id)}
                        className="bg-blue-500 hover:bg-blue-600 text-white py-1 px-4 rounded transition"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* -----------------------------
          Modal for Single Report
      ----------------------------- */}
      {isModalOpen && selectedReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-lg max-w-3xl w-full p-6 relative">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-3 right-3 text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>

            <div ref={reportRef}>
              <h2 className="text-2xl font-bold mb-4">Report Details</h2>

              {selectedReport.profile && (
                <div className="flex items-center mb-6">
                  <img
                    src={selectedReport.profile.picture?.data?.url}
                    className="w-16 h-16 rounded-full mr-4"
                    alt="Profile"
                  />
                  <div>
                    <p className="text-lg font-semibold">
                      {selectedReport.profile.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      Birthday: {selectedReport.profile.birthday || "N/A"}
                    </p>
                    <p className="text-sm text-gray-500">
                      Gender: {selectedReport.profile.gender || "N/A"}
                    </p>
                  </div>
                </div>
              )}

              {selectedReport.insightMetrics?.length > 0 && (
                <>
                  <h3 className="font-semibold mb-2">Insight Metrics</h3>
                  <ul className="list-disc ml-6 mb-4 text-gray-700">
                    {selectedReport.insightMetrics.map((m, i) => (
                      <li key={i}>
                        {m.title}: {m.value}%
                      </li>
                    ))}
                  </ul>
                </>
              )}

              {selectedReport.recommendations?.length > 0 && (
                <>
                  <h3 className="font-semibold mb-2">Recommendations</h3>
                  <ul className="list-disc ml-6 text-gray-700">
                    {selectedReport.recommendations.map((r, i) => (
                      <li key={i}>{r.text || r}</li>
                    ))}
                  </ul>
                </>
              )}
            </div>

            <div className="mt-6 flex gap-4">
              <button
                onClick={downloadReportAsPNG}
                className="bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded transition"
              >
                Download as PNG
              </button>
              <button
                onClick={() => navigator.share?.({
                  title: 'Report',
                  text: `Check out this report: ${selectedReport.report_id}`,
                })}
                className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded transition"
              >
                Share
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
