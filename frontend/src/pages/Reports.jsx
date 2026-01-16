import React, { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import AnalyzeToken from "../components/AnalyzeToken";
import * as htmlToImage from "html-to-image";
import download from "downloadjs";

const BACKEND_URL = "https://cyberhunk.onrender.com";

export default function ReportsPage({ token }) {
  const [profile, setProfile] = useState(null);
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  const [sortOrder, setSortOrder] = useState("newest");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);

  const reportRef = useRef(null);

  useEffect(() => {
    if (!profile?.id) return;

    const fetchReports = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${BACKEND_URL}/insights/reports/`, {
          params: { profile_id: String(profile.id) },
          withCredentials: true,
        });
        setReports(res.data?.reports || []);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, [profile?.id]);

  const processedReports = useMemo(() => {
    const list = [...reports];
    list.sort((a, b) =>
      sortOrder === "newest"
        ? new Date(b.created_at) - new Date(a.created_at)
        : new Date(a.created_at) - new Date(b.created_at)
    );
    return list;
  }, [reports, sortOrder]);

  const totalPages = Math.ceil(processedReports.length / pageSize);
  const paginatedReports = processedReports.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  const fetchReport = async (id) => {
    const res = await axios.get(
      `${BACKEND_URL}/insights/reports/${id}/`,
      { withCredentials: true }
    );
    setSelectedReport(res.data);
    setIsModalOpen(true);
  };

  const downloadReport = async () => {
    const dataUrl = await htmlToImage.toPng(reportRef.current);
    download(dataUrl, `report_${selectedReport.report_id}.png`);
  };

  const closeModal = (e) => {
    if (e.target.id === "modal") setIsModalOpen(false);
  };

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {!profile && (
          <AnalyzeToken
            token={token}
            onInsightsFetched={(d) => setProfile(d.profile)}
          />
        )}

        <h1 className="text-3xl font-bold text-indigo-700 mb-6">
          Result History
        </h1>

        <div className="flex flex-col sm:flex-row justify-between gap-4 mb-4">
          <div className="flex gap-3">
            <select
              value={sortOrder}
              onChange={(e) => {
                setSortOrder(e.target.value);
                setCurrentPage(1);
              }}
              className="border rounded-lg px-4 py-2 text-sm"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
            </select>

            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="border rounded-lg px-4 py-2 text-sm"
            >
              <option value={5}>5 / page</option>
              <option value={10}>10 / page</option>
              <option value={20}>20 / page</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto bg-white rounded-2xl shadow">
          <table className="min-w-full text-sm">
            <thead className="bg-indigo-50 text-indigo-700">
              <tr>
                <th className="px-4 py-3 text-left">No</th>
                <th className="px-4 py-3 text-left">Test Taken</th>
                <th className="px-4 py-3">Happy Posts</th>
                <th className="px-4 py-3">Good Posting Habits</th>
                <th className="px-4 py-3">Privacy Care</th>
                <th className="px-4 py-3">Being Respectful</th>
                <th className="px-4 py-3 text-center">Actions</th>
              </tr>
            </thead>

            <tbody>
              {paginatedReports.map((r, i) => {
                const metrics = Object.fromEntries(
                  (r.insightMetrics || []).map(m => [m.title, m.value])
                );

                return (
                  <tr key={r.report_id} className="border-t hover:bg-slate-50">
                    <td className="px-4 py-3">
                      {(currentPage - 1) * pageSize + i + 1}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {new Date(r.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "2-digit",
                        year: "numeric",
                      })}
                    </td>
                    <td className="px-4 py-3 text-center">{metrics["Happy Posts"] ?? "—"}%</td>
                    <td className="px-4 py-3 text-center">{metrics["Good Posting Habits"] ?? "—"}%</td>
                    <td className="px-4 py-3 text-center">{metrics["Privacy Care"] ?? "—"}%</td>
                    <td className="px-4 py-3 text-center">{metrics["Being Respectful"] ?? "—"}%</td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => fetchReport(r.report_id)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-1.5 rounded-lg text-xs font-semibold"
                      >
                        View More
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="mt-6 flex justify-center gap-2">
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(p => p - 1)}
              className="px-4 py-2 border rounded disabled:opacity-40"
            >
              Prev
            </button>

            {[...Array(totalPages)].map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentPage(i + 1)}
                className={`px-4 py-2 rounded ${
                  currentPage === i + 1
                    ? "bg-indigo-600 text-white"
                    : "border"
                }`}
              >
                {i + 1}
              </button>
            ))}

            <button
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage(p => p + 1)}
              className="px-4 py-2 border rounded disabled:opacity-40"
            >
              Next
            </button>
          </div>
        )}

        {isModalOpen && selectedReport && (
          <div
            id="modal"
            onClick={closeModal}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white w-full max-w-3xl rounded-3xl p-6 relative">
              <button
                onClick={() => setIsModalOpen(false)}
                className="absolute top-4 right-4 text-xl"
              >
                ×
              </button>

              <div ref={reportRef} className="space-y-6 p-6 bg-indigo-50 rounded-2xl">
                <h3 className="text-xl font-bold text-indigo-700">
                  Detailed Report
                </h3>

                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {selectedReport.insightMetrics.map((m, i) => (
                    <li key={i} className="bg-white p-4 rounded-xl shadow">
                      {m.title} — {m.value}%
                    </li>
                  ))}
                </ul>
              </div>

              <div className="mt-6 flex justify-end gap-3">
                <button
                  onClick={downloadReport}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-xl"
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
