import React, { useEffect, useState, useRef, useMemo } from "react";
import axios from "axios";
import AnalyzeToken from "../components/AnalyzeToken";
import * as htmlToImage from "html-to-image";
import download from "downloadjs";

const BACKEND_URL = "http://localhost:8000";
const PAGE_SIZE = 5;

export default function ReportsPage({ token }) {
  const [profile, setProfile] = useState(null);
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [statusFilter, setStatusFilter] = useState("all");
  const [sortOrder, setSortOrder] = useState("newest");
  const [currentPage, setCurrentPage] = useState(1);

  const reportRef = useRef(null);

  // Fetch reports
  useEffect(() => {
    const fetchReports = async () => {
      if (!profile?.id) {
        setReports([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const res = await axios.get(`${BACKEND_URL}/insights/reports/`, {
          params: { profile_id: String(profile.id) },
          withCredentials: true,
        });
        setReports(res.data?.reports || []);
      } catch {
        setError("Failed to load reports.");
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [profile?.id]);

  // Filter + Sort
  const processedReports = useMemo(() => {
    let list = [...reports];
    if (statusFilter !== "all") {
      list = list.filter((r) => (r.status || "Completed") === statusFilter);
    }
    list.sort((a, b) =>
      sortOrder === "newest"
        ? new Date(b.created_at) - new Date(a.created_at)
        : new Date(a.created_at) - new Date(b.created_at)
    );
    return list;
  }, [reports, statusFilter, sortOrder]);

  const totalPages = Math.ceil(processedReports.length / PAGE_SIZE);
  const paginatedReports = processedReports.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
  );

  const fetchReport = async (reportId) => {
    setLoading(true);
    try {
      const res = await axios.get(
        `${BACKEND_URL}/insights/reports/${reportId}/`,
        { withCredentials: true }
      );
      setSelectedReport(res.data);
      setIsModalOpen(true);
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
    if (e.target.id === "modal-backdrop") setIsModalOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {!profile && (
          <AnalyzeToken
            token={token}
            onInsightsFetched={(d) => setProfile(d.profile)}
          />
        )}

        {/* Header + Filters */}
        <div className="mt-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h2 className="text-2xl sm:text-3xl font-bold text-indigo-700">
            Past Reports
          </h2>
          <div className="flex flex-col sm:flex-row gap-3">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setCurrentPage(1);
              }}
              className="rounded-xl border px-4 py-2 text-sm shadow-sm focus:ring-2 focus:ring-indigo-400"
            >
              <option value="all">All Status</option>
              <option value="Completed">Completed</option>
            </select>
            <select
              value={sortOrder}
              onChange={(e) => {
                setSortOrder(e.target.value);
                setCurrentPage(1);
              }}
              className="rounded-xl border px-4 py-2 text-sm shadow-sm focus:ring-2 focus:ring-indigo-400"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
            </select>
          </div>
        </div>

        {/* Report Cards */}
        <div className="mt-6 space-y-4">
          {paginatedReports.map((r) => (
            <div
              key={r.report_id}
              className="bg-white rounded-2xl p-5 shadow-sm hover:shadow-md transition
                         flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
            >
              <div>
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
                  className="bg-indigo-600 hover:bg-indigo-700 text-white
                             px-5 py-2 rounded-xl text-sm font-semibold"
                >
                  View
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-8 flex justify-center items-center gap-2 flex-wrap">
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((p) => p - 1)}
              className="px-4 py-2 rounded-lg border disabled:opacity-40"
            >
              Previous
            </button>

            {[...Array(totalPages)].map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentPage(i + 1)}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  currentPage === i + 1
                    ? "bg-indigo-600 text-white"
                    : "border hover:bg-slate-100"
                }`}
              >
                {i + 1}
              </button>
            ))}

            <button
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage((p) => p + 1)}
              className="px-4 py-2 rounded-lg border disabled:opacity-40"
            >
              Next
            </button>
          </div>
        )}

        {/* Modal */}
        {isModalOpen && selectedReport && (
          <div
            id="modal-backdrop"
            onClick={closeOnBackdrop}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white w-full max-w-3xl rounded-3xl shadow-xl p-6 sm:p-8 max-h-[90vh] overflow-y-auto relative">
              <button
                onClick={() => setIsModalOpen(false)}
                className="absolute top-4 right-4 text-xl text-gray-500"
              >
                ×
              </button>

              {/* Export Area */}
              <div
                ref={reportRef}
                className="space-y-6 p-6 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl"
              >
                {/* Profile */}
                {selectedReport.profile && (
                  <div className="flex flex-col sm:flex-row items-center gap-4">
                    <img
                      src={selectedReport.profile.picture?.data?.url}
                      alt="Profile"
                      className="w-20 h-20 rounded-full border-4 border-indigo-300 shadow"
                    />
                    <div className="text-center sm:text-left">
                      <p className="font-bold text-xl">
                        {selectedReport.profile.name}
                      </p>
                      <p className="text-sm text-gray-600">
                        {selectedReport.profile.birthday || "N/A"}
                      </p>
                      <p className="text-sm text-gray-600">
                        {selectedReport.profile.gender || "N/A"}
                      </p>
                    </div>
                  </div>
                )}

                {/* Metrics */}
                {selectedReport.insightMetrics?.length > 0 && (
                  <div>
                    <h3 className="font-bold text-lg text-indigo-600 mb-2">
                      Insight Metrics
                    </h3>
                    <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {selectedReport.insightMetrics.map((m, i) => (
                        <li
                          key={i}
                          className="bg-white rounded-xl p-3 shadow text-gray-700 font-semibold"
                        >
                          {m.title} — {m.value}%
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {selectedReport.recommendations?.length > 0 && (
                  <div>
                    <h3 className="font-bold text-lg text-purple-600 mb-2">
                      Recommendations
                    </h3>
                    <ul className="space-y-2">
                      {selectedReport.recommendations.map((r, i) => (
                        <li
                          key={i}
                          className="bg-white rounded-xl p-3 shadow text-gray-700"
                        >
                          {r.text || r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Buttons */}
              <div className="mt-6 flex flex-col sm:flex-row justify-end gap-3">
                <button
                  onClick={shareReport}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-5 py-2 rounded-xl font-semibold"
                >
                  Share
                </button>
                <button
                  onClick={downloadReport}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-xl font-semibold"
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
