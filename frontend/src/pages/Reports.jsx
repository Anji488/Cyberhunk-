import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import AnalyzeToken from "../components/AnalyzeToken";
import * as htmlToImage from "html-to-image";
import download from "downloadjs";

const BACKEND_URL = "https://cyberhunk.onrender.com";

export default function ReportsPage({ token }) {
  const [profile, setProfile] = useState(null);
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const reportRef = useRef(null);

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
      } catch {
        setError("Failed to load reports.");
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [profile?.id]);

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
    } catch {
      setError("Unable to load report.");
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!reportRef.current) return;
    const dataUrl = await htmlToImage.toPng(reportRef.current);
    download(dataUrl, `report_${selectedReport.report_id}.png`);
  };

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

  const closeOnBackdrop = (e) => {
    if (e.target.id === "modal-backdrop") {
      setIsModalOpen(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 px-4 sm:px-6 py-8">
      <div className="max-w-6xl mx-auto">
        {!profile && (
          <AnalyzeToken
            token={token}
            onInsightsFetched={(data) => setProfile(data.profile)}
          />
        )}

        {loading && <p className="text-gray-500 mt-4">Loading…</p>}
        {error && <p className="text-red-600 font-medium mt-4">{error}</p>}

        {!loading && reports.length > 0 && (
          <div className="mt-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-indigo-700 mb-6">
              Past Reports
            </h2>

            <div className="grid gap-4">
              {reports.map((r) => (
                <div
                  key={r.report_id}
                  className="bg-white rounded-2xl p-5 shadow-sm
                             hover:shadow-md transition
                             flex flex-col sm:flex-row
                             sm:items-center sm:justify-between gap-4"
                >
                  <div className="min-w-0">
                    <p className="font-semibold text-gray-800 truncate">
                      {r.report_id}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(r.created_at).toLocaleString()}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-sm font-medium">
                      {r.status || "Completed"}
                    </span>

                    <button
                      onClick={() => fetchReport(r.report_id)}
                      className="bg-indigo-600 hover:bg-indigo-700
                                 text-white px-5 py-2 rounded-xl
                                 text-sm font-semibold transition"
                    >
                      View Report
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {isModalOpen && selectedReport && (
          <div
            id="modal-backdrop"
            onClick={closeOnBackdrop}
            className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm
                       flex items-center justify-center p-4"
          >
            <div className="bg-white w-full max-w-3xl rounded-3xl shadow-xl
                            max-h-[90vh] overflow-y-auto p-6 sm:p-8 relative">
              <button
                onClick={() => setIsModalOpen(false)}
                className="absolute top-4 right-4
                           text-gray-500 hover:text-gray-800
                           text-xl font-bold"
              >
                ×
              </button>

              <div
                ref={reportRef}
                className="space-y-6 bg-slate-50 rounded-2xl p-5 sm:p-6"
              >
                {selectedReport.profile && (
                  <div className="flex flex-col sm:flex-row items-center gap-4">
                    <img
                      src={selectedReport.profile.picture?.data?.url}
                      alt="Profile"
                      className="w-20 h-20 rounded-full object-cover border"
                    />
                    <div className="text-center sm:text-left">
                      <p className="text-lg font-semibold">
                        {selectedReport.profile.name}
                      </p>
                      <p className="text-sm text-gray-600">
                        {selectedReport.profile.birthday || "N/A"} ·{" "}
                        {selectedReport.profile.gender || "N/A"}
                      </p>
                    </div>
                  </div>
                )}

                {selectedReport.insightMetrics?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-indigo-700 mb-3">
                      Insight Metrics
                    </h3>
                    <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {selectedReport.insightMetrics.map((m, i) => (
                        <li
                          key={i}
                          className="bg-white rounded-xl p-3 shadow-sm
                                     text-gray-700 font-medium"
                        >
                          {m.title} — {m.value}%
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedReport.recommendations?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-purple-700 mb-3">
                      Recommendations
                    </h3>
                    <ul className="space-y-2">
                      {selectedReport.recommendations.map((r, i) => (
                        <li
                          key={i}
                          className="bg-white rounded-xl p-3 shadow-sm
                                     text-gray-700"
                        >
                          {r.text || r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="mt-6 flex flex-col sm:flex-row justify-end gap-3">
                <button
                  onClick={shareReport}
                  className="bg-purple-600 hover:bg-purple-700
                             text-white px-5 py-2 rounded-xl
                             font-semibold transition"
                >
                  Share
                </button>
                <button
                  onClick={downloadReport}
                  className="bg-indigo-600 hover:bg-indigo-700
                             text-white px-5 py-2 rounded-xl
                             font-semibold transition"
                >
                  Download
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
