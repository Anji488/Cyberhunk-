// frontend/src/pages/Reports.jsx
import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import AnalyzeToken from "../components/AnalyzeToken";
import * as htmlToImage from "html-to-image";
import download from "downloadjs";
import { Share2, Download } from "lucide-react";

const BACKEND_URL = "https://cyberhunk.onrender.com";

export default function ReportsPage({ token }) {
  const [profile, setProfile] = useState(null);
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const reportRef = useRef(null);

  // -----------------------------
  // Fetch reports
  // -----------------------------
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
        setReports(list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
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
      setIsModalOpen(true);
    } catch (err) {
      console.error("Error fetching report:", err);
      setError("Unable to load report.");
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------
  // Download report as PNG
  // -----------------------------
  const downloadReport = async () => {
    if (!reportRef.current) return;
    try {
      const dataUrl = await htmlToImage.toPng(reportRef.current);
      download(dataUrl, `report_${selectedReport.report_id}.png`);
    } catch (err) {
      console.error("Download failed:", err);
    }
  };

  // -----------------------------
  // Share report
  // -----------------------------
  const shareReport = async () => {
    if (!reportRef.current) return;
    try {
      const dataUrl = await htmlToImage.toPng(reportRef.current);
      const blob = await (await fetch(dataUrl)).blob();
      const file = new File([blob], `report_${selectedReport.report_id}.png`, { type: blob.type });

      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({
          title: "Report",
          text: "Check out this report!",
          files: [file],
        });
      } else {
        alert("This device does not support sharing. Try downloading instead.");
      }
    } catch (err) {
      console.error("Share failed:", err);
    }
  };

  // -----------------------------
  // Render
  // -----------------------------
  return (
    <div className="max-w-6xl mx-auto p-6 text-gray-800 bg-gray-50 min-h-screen">
      {!profile && (
        <AnalyzeToken
          token={token}
          onInsightsFetched={(data) => setProfile(data.profile)}
        />
      )}

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
                  <tr key={r.report_id} className="border-b hover:bg-gray-100 transition">
                    <td className="py-3 px-6">{r.report_id}</td>
                    <td className="py-3 px-6">{new Date(r.created_at).toLocaleString()}</td>
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
          Modal for Report
      ----------------------------- */}
      {isModalOpen && selectedReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-3xl w-full p-6 relative">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-3 right-3 text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>

            {/* Export area */}
            <div ref={reportRef} className="space-y-4 p-4 bg-gray-50 rounded-xl">
              {selectedReport.profile && (
                <div className="flex items-center gap-4">
                  <img
                    src={selectedReport.profile.picture?.data?.url}
                    alt="Profile"
                    className="w-16 h-16 rounded-full border border-gray-300"
                  />
                  <div>
                    <p className="font-semibold">{selectedReport.profile.name}</p>
                    <p className="text-gray-500 text-sm">
                      Birthday: {selectedReport.profile.birthday || "N/A"}
                    </p>
                    <p className="text-gray-500 text-sm">
                      Gender: {selectedReport.profile.gender || "N/A"}
                    </p>
                  </div>
                </div>
              )}

              {selectedReport.insightMetrics?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">Insight Metrics</h3>
                  <ul className="list-disc ml-6 text-gray-600">
                    {selectedReport.insightMetrics.map((m, idx) => (
                      <li key={idx}>{m.title}: {m.value}%</li>
                    ))}
                  </ul>
                </div>
              )}

              {selectedReport.recommendations?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-700 mb-2">Recommendations</h3>
                  <ul className="list-disc ml-6 text-gray-600">
                    {selectedReport.recommendations.map((r, idx) => (
                      <li key={idx}>{r.text || r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Buttons */}
            <div className="mt-4 flex gap-3 justify-end">
              <button
                onClick={shareReport}
                className="flex items-center gap-2 bg-purple-500 text-white px-4 py-2 rounded-xl hover:bg-purple-600 transition"
              >
                <Share2 className="w-5 h-5" /> Share
              </button>
              <button
                onClick={downloadReport}
                className="flex items-center gap-2 bg-indigo-500 text-white px-4 py-2 rounded-xl hover:bg-indigo-600 transition"
              >
                <Download className="w-5 h-5" /> Download
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
