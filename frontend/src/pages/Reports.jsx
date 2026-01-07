import React, { useEffect, useState, useRef, useMemo } from "react";
import axios from "axios";
import AnalyzeToken from "../components/AnalyzeToken";
import * as htmlToImage from "html-to-image";
import download from "downloadjs";

const BACKEND_URL = "https://cyberhunk.onrender.com";
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
    const dataUrl = await htmlToImage.toPng(reportRef.current);
    download(dataUrl, `report_${selectedReport.report_id}.png`);
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

        {/* Header */}
        <div className="mt-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <h2 className="text-2xl sm:text-3xl font-bold text-indigo-700">
            Past Reports
          </h2>

          {/* Filters */}
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

        {/* Report List */}
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
            <div className="bg-white max-w-3xl w-full rounded-3xl p-6 shadow-xl max-h-[90vh] overflow-y-auto relative">
              <button
                onClick={() => setIsModalOpen(false)}
                className="absolute top-4 right-4 text-xl text-gray-500"
              >
                ×
              </button>

              <div ref={reportRef} className="space-y-6 bg-slate-50 p-6 rounded-2xl">
                <h3 className="text-xl font-bold text-indigo-700">
                  Report Details
                </h3>

                {selectedReport.insightMetrics?.map((m, i) => (
                  <div
                    key={i}
                    className="bg-white p-3 rounded-xl shadow-sm"
                  >
                    {m.title} — {m.value}%
                  </div>
                ))}
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={downloadReport}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-xl font-semibold"
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
