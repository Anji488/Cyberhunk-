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
        setReports(
          list.sort(
            (a, b) => new Date(b.created_at) - new Date(a.created_at)
          )
        );
      } catch (err) {
        console.error(err);
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
    setLoading(true);
    setError(null);

    try {
      const res = await axios.get(
        `${BACKEND_URL}/insights/reports/${reportId}/`,
        { withCredentials: true }
      );
      setSelectedReport(res.data);
      setIsModalOpen(true);
    } catch (err) {
      console.error(err);
      setError("Unable to load report.");
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------
  // Download report
  // -----------------------------
  const downloadReport = async () => {
    if (!reportRef.current) return;
    const dataUrl = await htmlToImage.toPng(reportRef.current);
    download(dataUrl, `report_${selectedReport.report_id}.png`);
  };

  // -----------------------------
  // Share report
  // -----------------------------
  const shareReport = async () => {
    if (!reportRef.current) return;

    const dataUrl = await htmlToImage.toPng(reportRef.current);
    const blob = await (await fetch(dataUrl)).blob();
    const file = new File([blob], "report.png", { type: blob.type });

    if (navigator.canShare?.({ files: [file] })) {
      await navigator.share({
        title: "Report",
        text: "Check out this report!",
        files: [file],
      });
    } else {
      alert("Sharing not supported. Please download instead.");
    }
  };

  // -----------------------------
  // Close modal on outside click
  // -----------------------------
  const closeOnBackdrop = (e) => {
    if (e.target.id === "modal-backdrop") {
      setIsModalOpen(false);
    }
  };

  // -----------------------------
  // Render
  // -----------------------------
  return (
    <div className="max-w-6xl mx-auto p-6 min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50">
      {!profile && (
        <AnalyzeToken
          token={token}
          onInsightsFetched={(data) => setProfile(data.profile)}
        />
      )}

      {loading && <p className="text-gray-500">Loading...</p>}
      {error && <p className="text-red-600 font-bold">{error}</p>}

      {/* -----------------------------
          Cartoon Report Cards
      ----------------------------- */}
      {!loading && reports.length > 0 && (
        <div className="mt-8">
          <h2 className="text-3xl font-extrabold mb-6 text-indigo-600">
            📊 Past Reports
          </h2>

          <div className="grid gap-4">
            {reports.map((r) => (
              <div
                key={r.report_id}
                className="bg-gradient-to-r from-white to-indigo-50
                           rounded-2xl p-5 shadow-md
                           hover:shadow-xl hover:-translate-y-1
                           transition-all duration-300
                           flex items-center justify-between"
              >
                <div>
                  <p className="font-bold text-gray-800 truncate max-w-xs">
                    🧾 {r.report_id}
                  </p>
                  <p className="text-sm text-gray-500">
                    ⏰ {new Date(r.created_at).toLocaleString()}
                  </p>
                </div>

                <span className="px-3 py-1 rounded-full bg-green-100 text-green-700 font-semibold">
                  {r.status || "Completed"}
                </span>

                <button
                  onClick={() => fetchReport(r.report_id)}
                  className="ml-4 bg-indigo-500 hover:bg-indigo-600
                             text-white px-5 py-2 rounded-xl
                             font-semibold shadow transition"
                >
                  View ✨
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* -----------------------------
          Animated Modal
      ----------------------------- */}
      {isModalOpen && selectedReport && (
        <div
          id="modal-backdrop"
          onClick={closeOnBackdrop}
          className="fixed inset-0 z-50 flex items-center justify-center
                     bg-gradient-to-br from-indigo-300/40 via-purple-300/40 to-pink-300/40
                     backdrop-blur-sm p-4"
        >
          <div className="relative bg-white/90 backdrop-blur-xl
                          rounded-3xl shadow-2xl
                          max-w-3xl w-full p-8
                          animate-scaleIn">
            {/* Close */}
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute -top-4 -right-4
                         bg-red-500 hover:bg-red-600
                         text-white w-10 h-10 rounded-full
                         flex items-center justify-center
                         shadow-lg text-lg"
            >
              ✖
            </button>

            {/* Export Area */}
            <div
              ref={reportRef}
              className="space-y-6 p-6 bg-gradient-to-br
                         from-indigo-50 to-purple-50 rounded-2xl"
            >
              {/* Profile */}
              {selectedReport.profile && (
                <div className="flex items-center gap-4">
                  <img
                    src={selectedReport.profile.picture?.data?.url}
                    alt="Profile"
                    className="w-20 h-20 rounded-full border-4 border-indigo-300 shadow"
                  />
                  <div>
                    <p className="font-bold text-xl">
                      {selectedReport.profile.name}
                    </p>
                    <p className="text-sm text-gray-600">
                      🎂 {selectedReport.profile.birthday || "N/A"}
                    </p>
                    <p className="text-sm text-gray-600">
                      ⚧ {selectedReport.profile.gender || "N/A"}
                    </p>
                  </div>
                </div>
              )}

              {/* Metrics */}
              {selectedReport.insightMetrics?.length > 0 && (
                <div>
                  <h3 className="font-bold text-lg text-indigo-600 mb-2">
                    📈 Insight Metrics
                  </h3>
                  <ul className="grid grid-cols-2 gap-3">
                    {selectedReport.insightMetrics.map((m, i) => (
                      <li
                        key={i}
                        className="bg-white rounded-xl p-3 shadow text-gray-700 font-semibold"
                      >
                        {m.title} – {m.value}%
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Recommendations */}
              {selectedReport.recommendations?.length > 0 && (
                <div>
                  <h3 className="font-bold text-lg text-purple-600 mb-2">
                    💡 Recommendations
                  </h3>
                  <ul className="space-y-2">
                    {selectedReport.recommendations.map((r, i) => (
                      <li
                        key={i}
                        className="bg-white rounded-xl p-3 shadow text-gray-700"
                      >
                        👉 {r.text || r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Buttons */}
            <div className="mt-6 flex justify-end gap-4">
              <button
                onClick={shareReport}
                className="flex items-center gap-2
                           bg-gradient-to-r from-purple-500 to-pink-500
                           text-white px-5 py-2 rounded-xl
                           font-semibold shadow hover:scale-105 transition"
              >
                <Share2 className="w-5 h-5" /> Share
              </button>
              <button
                onClick={downloadReport}
                className="flex items-center gap-2
                           bg-gradient-to-r from-indigo-500 to-blue-500
                           text-white px-5 py-2 rounded-xl
                           font-semibold shadow hover:scale-105 transition"
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
