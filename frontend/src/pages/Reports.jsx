import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import AnalyzeToken from "../components/AnalyzeToken";
import * as htmlToImage from "html-to-image";
import download from "downloadjs";
import { Share2, Download, ChevronLeft, ChevronRight } from "lucide-react";

const BACKEND_URL = "https://cyberhunk.onrender.com";
const PAGE_SIZE = 5; // 👈 change if needed

export default function ReportsPage({ token }) {
  const [profile, setProfile] = useState(null);
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  const reportRef = useRef(null);

  // -----------------------------
  // Fetch reports
  // -----------------------------
  useEffect(() => {
    const fetchReports = async () => {
      if (!profile?.id) return;

      setLoading(true);
      try {
        const res = await axios.get(`${BACKEND_URL}/insights/reports/`, {
          params: { profile_id: String(profile.id) },
          withCredentials: true,
        });

        const sorted = (res.data?.reports || []).sort(
          (a, b) => new Date(b.created_at) - new Date(a.created_at)
        );

        setReports(sorted);
      } catch (err) {
        setError("Failed to load reports");
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [profile?.id]);

  // -----------------------------
  // Pagination
  // -----------------------------
  const totalPages = Math.ceil(reports.length / PAGE_SIZE);
  const start = (currentPage - 1) * PAGE_SIZE;
  const paginatedReports = reports.slice(start, start + PAGE_SIZE);

  // -----------------------------
  // Fetch single report
  // -----------------------------
  const fetchReport = async (id) => {
    try {
      const res = await axios.get(
        `${BACKEND_URL}/insights/reports/${id}/`,
        { withCredentials: true }
      );
      setSelectedReport(res.data);
      setIsModalOpen(true);
    } catch {
      setError("Unable to load report");
    }
  };

  // -----------------------------
  // Download / Share
  // -----------------------------
  const downloadReport = async () => {
    const dataUrl = await htmlToImage.toPng(reportRef.current);
    download(dataUrl, `report_${selectedReport.report_id}.png`);
  };

  const shareReport = async () => {
    const dataUrl = await htmlToImage.toPng(reportRef.current);
    const blob = await (await fetch(dataUrl)).blob();
    const file = new File([blob], "report.png", { type: blob.type });

    if (navigator.canShare?.({ files: [file] })) {
      navigator.share({ title: "Report", files: [file] });
    } else {
      alert("Sharing not supported");
    }
  };

  // -----------------------------
  // Close modal on backdrop
  // -----------------------------
  const closeOnBackdrop = (e) => {
    if (e.target.id === "modal-backdrop") setIsModalOpen(false);
  };

  // -----------------------------
  // Render
  // -----------------------------
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 p-4 sm:p-8">
      {!profile && (
        <AnalyzeToken token={token} onInsightsFetched={(d) => setProfile(d.profile)} />
      )}

      {loading && <p className="text-gray-500">Loading...</p>}
      {error && <p className="text-red-600 font-bold">{error}</p>}

      {/* -----------------------------
          Reports List
      ----------------------------- */}
      {!loading && paginatedReports.length > 0 && (
        <>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-indigo-600 mb-6">
            📊 Past Reports
          </h2>

          {/* Cards */}
          <div className="grid gap-4">
            {paginatedReports.map((r) => (
              <div
                key={r.report_id}
                className="bg-white rounded-2xl shadow-md p-4 sm:p-6
                           flex flex-col sm:flex-row sm:items-center
                           justify-between gap-4 hover:shadow-xl transition"
              >
                <div>
                  <p className="font-bold text-gray-800 truncate max-w-xs">
                    🧾 {r.report_id}
                  </p>
                  <p className="text-sm text-gray-500">
                    ⏰ {new Date(r.created_at).toLocaleString()}
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <span className="px-3 py-1 text-sm rounded-full bg-green-100 text-green-700 font-semibold">
                    {r.status || "Completed"}
                  </span>
                  <button
                    onClick={() => fetchReport(r.report_id)}
                    className="bg-indigo-500 hover:bg-indigo-600
                               text-white px-4 py-2 rounded-xl font-semibold"
                  >
                    View ✨
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          <div className="mt-6 flex justify-center items-center gap-4">
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((p) => p - 1)}
              className="p-2 rounded-full bg-white shadow disabled:opacity-40"
            >
              <ChevronLeft />
            </button>

            <span className="font-semibold text-gray-700">
              Page {currentPage} of {totalPages}
            </span>

            <button
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage((p) => p + 1)}
              className="p-2 rounded-full bg-white shadow disabled:opacity-40"
            >
              <ChevronRight />
            </button>
          </div>
        </>
      )}

      {/* -----------------------------
          Responsive Modal
      ----------------------------- */}
      {isModalOpen && selectedReport && (
        <div
          id="modal-backdrop"
          onClick={closeOnBackdrop}
          className="fixed inset-0 z-50 flex items-center justify-center
                     bg-black/40 backdrop-blur-sm p-4"
        >
          <div className="relative bg-white rounded-3xl shadow-2xl
                          w-full max-w-3xl max-h-[90vh] overflow-y-auto p-6">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-3 right-3 bg-red-500 text-white
                         w-9 h-9 rounded-full flex items-center justify-center"
            >
              ✖
            </button>

            <div ref={reportRef} className="space-y-6">
              <h3 className="text-xl font-bold text-indigo-600">
                📄 Report Details
              </h3>

              {selectedReport.insightMetrics?.length > 0 && (
                <div className="grid sm:grid-cols-2 gap-3">
                  {selectedReport.insightMetrics.map((m, i) => (
                    <div key={i} className="bg-indigo-50 rounded-xl p-3 font-semibold">
                      {m.title} – {m.value}%
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-6 flex flex-col sm:flex-row justify-end gap-3">
              <button
                onClick={shareReport}
                className="flex items-center justify-center gap-2
                           bg-purple-500 text-white px-4 py-2 rounded-xl"
              >
                <Share2 size={18} /> Share
              </button>
              <button
                onClick={downloadReport}
                className="flex items-center justify-center gap-2
                           bg-indigo-500 text-white px-4 py-2 rounded-xl"
              >
                <Download size={18} /> Download
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
