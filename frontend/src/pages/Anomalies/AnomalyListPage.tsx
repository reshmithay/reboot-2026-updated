import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { DataTable, Pagination } from "../../components/Common/DataTable";
import { RiskBadge, StatusBadge } from "../../components/Common/Badges";
import { FilterDropdown } from "../../components/Common/SearchBar";
import { AnomalyResult } from "../../types/anomaly.types";
import anomalyService from "../../services/anomaly/anomalyService";
import { format, subDays } from "date-fns";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import { message, Modal, Button } from "antd";

const AnomalyListPage: React.FC = () => {
  const [anomalies, setAnomalies] = useState<AnomalyResult[]>([]);
  const [stats, setStats] = useState({
    total_anomalies: 0,
    critical: 0,
    under_review: 0,
    avg_anomaly_score: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10); // <-- Make pageSize stateful
  const [filters, setFilters] = useState<{
    severity?: string;
    review_status?: string;
    anomaly_category?: string;
  }>({});

  // Fetch anomalies from API
  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await anomalyService.listResults({
          page: currentPage,
          page_size: pageSize,
          severity: filters.severity,
          review_status: filters.review_status,
          anomaly_category: filters.anomaly_category,
        });
        setAnomalies(response.items);
        setTotal(response.total);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to fetch anomalies",
        );
        console.error("Failed to fetch anomalies:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnomalies();
  }, [currentPage, pageSize, filters]);

  // Fetch statistics (only once on mount)
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const statsData = await anomalyService.getStats();
        setStats({
          total_anomalies: statsData.total_anomalies || 0,
          critical: statsData.critical || 0,
          under_review: statsData.under_review || 0,
          avg_anomaly_score: statsData.avg_anomaly_score || 0,
        });
      } catch (err) {
        console.error("Failed to fetch stats:", err);
        // Don't show error for stats, just use defaults
      }
    };

    fetchStats();
  }, []); // Only fetch once on mount

  // Filter options
  const severityOptions = [
    { label: "All", value: "" },
    { label: "Critical", value: "CRITICAL" },
    { label: "High", value: "HIGH" },
    { label: "Medium", value: "MEDIUM" },
    { label: "Low", value: "LOW" },
  ];

  const statusOptions = [
    { label: "All", value: "" },
    { label: "Pending", value: "PENDING" },
    { label: "Under Review", value: "UNDER_REVIEW" },
    { label: "Approved", value: "APPROVED" },
    { label: "Rejected", value: "REJECTED" },
  ];

  const categoryOptions = [
    { label: "All", value: "" },
    { label: "Fraud", value: "FRAUD" },
    { label: "Risk", value: "RISK" },
    { label: "Compliance", value: "COMPLIANCE" },
    { label: "Suspicious", value: "SUSPICIOUS" },
  ];

  const totalPages = Math.ceil(total / pageSize);

  // 30-Day Audit Report Generation
  const generate30DayAuditReport = async (exportFormat: "pdf" | "csv") => {
    try {
      message.loading({
        content: "Generating 30-day audit report...",
        key: "audit-report",
      });

      // Calculate date range (last 30 days)
      const endDate = new Date();
      const startDate = subDays(endDate, 30);

      // Fetch anomalies from the last 30 days using database filtering
      const response = await anomalyService.listResults({
        page: 1,
        page_size: 10000, // Large number to get all records in date range
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
      });

      const last30DaysAnomalies = response.items;

      if (last30DaysAnomalies.length === 0) {
        message.warning({
          content: "No anomalies found in the last 30 days",
          key: "audit-report",
        });
        return;
      }

      // Calculate audit statistics in a single pass for better performance
      const auditStats = last30DaysAnomalies.reduce(
        (stats, anomaly) => {
          // Count by severity
          if (anomaly.severity === "CRITICAL") stats.critical++;
          else if (anomaly.severity === "HIGH") stats.high++;
          else if (anomaly.severity === "MEDIUM") stats.medium++;
          else if (anomaly.severity === "LOW") stats.low++;

          // Count by review status
          if (anomaly.reviewStatus === "PENDING") stats.pending++;
          else if (anomaly.reviewStatus === "UNDER_REVIEW") stats.underReview++;
          else if (anomaly.reviewStatus === "APPROVED") stats.approved++;
          else if (anomaly.reviewStatus === "REJECTED") stats.rejected++;

          // Accumulate totals
          stats.totalAmount += anomaly.amount || 0;
          stats.totalRiskScore += anomaly.anomalyScore;

          return stats;
        },
        {
          total: last30DaysAnomalies.length,
          critical: 0,
          high: 0,
          medium: 0,
          low: 0,
          pending: 0,
          underReview: 0,
          approved: 0,
          rejected: 0,
          totalAmount: 0,
          totalRiskScore: 0,
          avgRiskScore: 0,
        },
      );

      // Calculate average after accumulation
      auditStats.avgRiskScore =
        auditStats.totalRiskScore / last30DaysAnomalies.length;

      if (exportFormat === "pdf") {
        generatePDFReport(last30DaysAnomalies, auditStats, startDate, endDate);
      } else {
        generateCSVReport(last30DaysAnomalies, auditStats, startDate, endDate);
      }

      message.success({
        content: `30-day audit report exported successfully (${last30DaysAnomalies.length} records)`,
        key: "audit-report",
      });
    } catch (error) {
      console.error("Error generating audit report:", error);
      message.error({
        content: "Failed to generate audit report",
        key: "audit-report",
      });
    }
  };

  const generatePDFReport = (
    anomalies: AnomalyResult[],
    stats: any,
    startDate: Date,
    endDate: Date,
  ) => {
    const doc = new jsPDF("landscape");
    let yPos = 20;
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 15;

    // Title Page
    doc.setFillColor(37, 99, 235);
    doc.rect(0, 0, pageWidth, 50, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont("helvetica", "bold");
    doc.text("30-DAY ANOMALY AUDIT REPORT", pageWidth / 2, 25, {
      align: "center",
    });
    doc.setFontSize(12);
    doc.text("Blockchain Anomaly Detection System", pageWidth / 2, 35, {
      align: "center",
    });
    doc.text(
      `${format(startDate, "MMM dd, yyyy")} - ${format(endDate, "MMM dd, yyyy")}`,
      pageWidth / 2,
      43,
      { align: "center" },
    );

    yPos = 60;
    doc.setTextColor(0, 0, 0);

    // Report Metadata
    doc.setFontSize(10);
    doc.text(
      `Report Generated: ${format(new Date(), "MMM dd, yyyy HH:mm")}`,
      margin,
      yPos,
    );
    doc.text(
      `Total Records: ${anomalies.length}`,
      pageWidth - margin - 50,
      yPos,
      { align: "right" },
    );
    yPos += 10;

    // Executive Summary Section
    doc.setFillColor(240, 240, 240);
    doc.rect(margin, yPos - 5, pageWidth - 2 * margin, 8, "F");
    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.text("EXECUTIVE SUMMARY", margin + 5, yPos);
    yPos += 12;

    // Summary Statistics Table
    autoTable(doc, {
      startY: yPos,
      head: [["Metric", "Count", "Percentage"]],
      body: [
        ["Total Anomalies Detected", stats.total.toString(), "100%"],
        [
          "Critical Severity",
          stats.critical.toString(),
          `${((stats.critical / stats.total) * 100).toFixed(1)}%`,
        ],
        [
          "High Severity",
          stats.high.toString(),
          `${((stats.high / stats.total) * 100).toFixed(1)}%`,
        ],
        [
          "Medium Severity",
          stats.medium.toString(),
          `${((stats.medium / stats.total) * 100).toFixed(1)}%`,
        ],
        [
          "Low Severity",
          stats.low.toString(),
          `${((stats.low / stats.total) * 100).toFixed(1)}%`,
        ],
        ["", "", ""],
        [
          "Pending Review",
          stats.pending.toString(),
          `${((stats.pending / stats.total) * 100).toFixed(1)}%`,
        ],
        [
          "Under Review",
          stats.underReview.toString(),
          `${((stats.underReview / stats.total) * 100).toFixed(1)}%`,
        ],
        [
          "Approved",
          stats.approved.toString(),
          `${((stats.approved / stats.total) * 100).toFixed(1)}%`,
        ],
        [
          "Rejected",
          stats.rejected.toString(),
          `${((stats.rejected / stats.total) * 100).toFixed(1)}%`,
        ],
        ["", "", ""],
        ["Total Amount Involved", `${stats.totalAmount.toLocaleString()}`, "-"],
        [
          "Average Risk Score",
          `${(stats.avgRiskScore * 100).toFixed(1)}%`,
          "-",
        ],
      ],
      theme: "grid",
      headStyles: {
        fillColor: [37, 99, 235],
        textColor: 255,
        fontStyle: "bold",
      },
      margin: { left: margin, right: margin },
      columnStyles: {
        0: { cellWidth: 100 },
        1: { cellWidth: 50, halign: "right" },
        2: { cellWidth: 50, halign: "right" },
      },
    });

    yPos = (doc as any).lastAutoTable.finalY + 15;

    // Detailed Anomaly Records
    doc.addPage();
    yPos = 20;
    doc.setFillColor(240, 240, 240);
    doc.rect(margin, yPos - 5, pageWidth - 2 * margin, 8, "F");
    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.text("DETAILED ANOMALY RECORDS", margin + 5, yPos);
    yPos += 10;

    // Anomaly Details Table
    autoTable(doc, {
      startY: yPos,
      head: [
        [
          "ID",
          "Date",
          "Severity",
          "Category",
          "Risk Score",
          "Amount",
          "Status",
          "Assigned To",
        ],
      ],
      body: anomalies.map((a) => [
        a.anomalyId.substring(0, 8),
        format(new Date(a.createdAt), "MMM dd, yyyy"),
        a.severity,
        a.anomalyCategory,
        `${(a.anomalyScore * 100).toFixed(0)}%`,
        `${a.currency || ""} ${a.amount?.toLocaleString() || "-"}`,
        a.reviewStatus,
        a.assignedTo || "Unassigned",
      ]),
      theme: "striped",
      headStyles: {
        fillColor: [37, 99, 235],
        textColor: 255,
        fontStyle: "bold",
        fontSize: 8,
      },
      bodyStyles: { fontSize: 7 },
      margin: { left: margin, right: margin },
      columnStyles: {
        0: { cellWidth: 20 },
        1: { cellWidth: 28 },
        2: { cellWidth: 22 },
        3: { cellWidth: 25 },
        4: { cellWidth: 22 },
        5: { cellWidth: 30 },
        6: { cellWidth: 25 },
        7: { cellWidth: 25 },
      },
    });

    // Severity Breakdown by Category
    doc.addPage();
    yPos = 20;
    doc.setFillColor(240, 240, 240);
    doc.rect(margin, yPos - 5, pageWidth - 2 * margin, 8, "F");
    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.text("CATEGORY ANALYSIS", margin + 5, yPos);
    yPos += 10;

    const categories = Array.from(
      new Set(anomalies.map((a) => a.anomalyCategory)),
    );
    const categoryBreakdown = categories.map((cat) => {
      const catAnomalies = anomalies.filter((a) => a.anomalyCategory === cat);
      return [
        cat,
        catAnomalies.length.toString(),
        catAnomalies.filter((a) => a.severity === "CRITICAL").length.toString(),
        catAnomalies.filter((a) => a.severity === "HIGH").length.toString(),
        catAnomalies.filter((a) => a.severity === "MEDIUM").length.toString(),
        catAnomalies.filter((a) => a.severity === "LOW").length.toString(),
        `${((catAnomalies.reduce((sum, a) => sum + a.anomalyScore, 0) / catAnomalies.length) * 100).toFixed(1)}%`,
      ];
    });

    autoTable(doc, {
      startY: yPos,
      head: [
        ["Category", "Total", "Critical", "High", "Medium", "Low", "Avg Score"],
      ],
      body: categoryBreakdown,
      theme: "grid",
      headStyles: {
        fillColor: [37, 99, 235],
        textColor: 255,
        fontStyle: "bold",
      },
      margin: { left: margin, right: margin },
    });

    // Footer on all pages
    const pageCount = doc.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(128, 128, 128);
      doc.text(
        `Page ${i} of ${pageCount} | Confidential - For Regulatory Submission | Generated: ${format(new Date(), "MMM dd, yyyy HH:mm")}`,
        pageWidth / 2,
        doc.internal.pageSize.getHeight() - 10,
        { align: "center" },
      );
    }

    // Download PDF
    doc.save(
      `30Day_Audit_Report_${format(startDate, "yyyyMMdd")}_${format(endDate, "yyyyMMdd")}.pdf`,
    );
  };

  const generateCSVReport = (
    anomalies: AnomalyResult[],
    stats: any,
    startDate: Date,
    endDate: Date,
  ) => {
    // CSV Headers
    const headers = [
      "Anomaly ID",
      "Transaction ID",
      "Transaction Hash",
      "Client ID",
      "Amount",
      "Currency",
      "From Account",
      "To Account",
      "Transaction Type",
      "Anomaly Score",
      "Severity",
      "Category",
      "Anomaly Types",
      "Confidence",
      "Review Status",
      "Assigned To",
      "Detected At",
      "Created At",
      "Anomaly Reasons",
    ];

    // CSV Rows
    const rows = anomalies.map((a) => [
      a.anomalyId,
      a.transactionId,
      a.transactionHash,
      a.clientId || "",
      a.amount || "",
      a.currency || "",
      a.fromAccount || "",
      a.toAccount || "",
      a.transactionType || "",
      (a.anomalyScore * 100).toFixed(2),
      a.severity,
      a.anomalyCategory,
      a.anomalyTypes.join("; "),
      (a.confidence * 100).toFixed(2),
      a.reviewStatus,
      a.assignedTo || "Unassigned",
      format(new Date(a.detectedAt), "yyyy-MM-dd HH:mm:ss"),
      format(new Date(a.createdAt), "yyyy-MM-dd HH:mm:ss"),
      a.anomalyReasons
        .map((r) => `${r.reasonCode}: ${r.description}`)
        .join(" | "),
    ]);

    // Summary section at the top
    const summaryRows = [
      ["30-DAY ANOMALY AUDIT REPORT"],
      [
        `Report Period: ${format(startDate, "MMM dd, yyyy")} - ${format(endDate, "MMM dd, yyyy")}`,
      ],
      [`Generated: ${format(new Date(), "MMM dd, yyyy HH:mm:ss")}`],
      [""],
      ["EXECUTIVE SUMMARY"],
      [`Total Anomalies: ${stats.total}`],
      [
        `Critical Severity: ${stats.critical} (${((stats.critical / stats.total) * 100).toFixed(1)}%)`,
      ],
      [
        `High Severity: ${stats.high} (${((stats.high / stats.total) * 100).toFixed(1)}%)`,
      ],
      [
        `Medium Severity: ${stats.medium} (${((stats.medium / stats.total) * 100).toFixed(1)}%)`,
      ],
      [
        `Low Severity: ${stats.low} (${((stats.low / stats.total) * 100).toFixed(1)}%)`,
      ],
      [`Pending Review: ${stats.pending}`],
      [`Under Review: ${stats.underReview}`],
      [`Approved: ${stats.approved}`],
      [`Rejected: ${stats.rejected}`],
      [`Total Amount: ${stats.totalAmount.toLocaleString()}`],
      [`Average Risk Score: ${(stats.avgRiskScore * 100).toFixed(1)}%`],
      [""],
      ["DETAILED RECORDS"],
      headers,
    ];

    // Combine all rows
    const csvContent = [...summaryRows, ...rows]
      .map((row) =>
        row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","),
      )
      .join("\n");

    // Create blob and download
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `30Day_Audit_Report_${format(startDate, "yyyyMMdd")}_${format(endDate, "yyyyMMdd")}.csv`,
    );
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const showExportModal = () => {
    Modal.info({
      title: "Export 30-Day Audit Report",
      content: (
        <div>
          <p style={{ marginBottom: 16 }}>
            Select the format for your regulatory audit report. This will
            include all anomalies detected in the last 30 days.
          </p>
          <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
            <Button
              type="primary"
              onClick={() => {
                Modal.destroyAll();
                generate30DayAuditReport("pdf");
              }}
              style={{ flex: 1 }}
            >
              Export as PDF
            </Button>
            <Button
              onClick={() => {
                Modal.destroyAll();
                generate30DayAuditReport("csv");
              }}
              style={{ flex: 1 }}
            >
              Export as CSV
            </Button>
          </div>
        </div>
      ),
      centered: true,
      width: 500,
      okText: "Close",
      okButtonProps: { style: { display: "none" } },
      closable: true,
      maskClosable: true,
    });
  };

  // Table columns
  const columns = [
    {
      key: "anomalyId",
      header: "Anomaly ID",
      render: (anomaly: AnomalyResult) => (
        <span className="font-mono text-sm text-blue-600 hover:text-blue-800 cursor-pointer">
          {anomaly.anomalyId}
        </span>
      ),
    },
    {
      key: "transactionHash",
      header: "Transaction Hash",
      render: (anomaly: AnomalyResult) => (
        <span className="font-mono text-xs text-gray-600">
          {anomaly.transactionHash.substring(0, 16)}...
        </span>
      ),
    },
    {
      key: "severity",
      header: "Severity",
      render: (anomaly: AnomalyResult) => (
        <RiskBadge severity={anomaly.severity} />
      ),
    },
    {
      key: "category",
      header: "Category",
      render: (anomaly: AnomalyResult) => (
        <StatusBadge status={anomaly.anomalyCategory} />
      ),
    },
    {
      key: "anomalyScore",
      header: "Risk Score",
      render: (anomaly: AnomalyResult) => (
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                anomaly.anomalyScore > 0.8
                  ? "bg-red-600"
                  : anomaly.anomalyScore > 0.6
                    ? "bg-orange-500"
                    : anomaly.anomalyScore > 0.4
                      ? "bg-yellow-500"
                      : "bg-green-500"
              }`}
              style={{ width: `${anomaly.anomalyScore * 100}%` }}
            />
          </div>
          <span className="text-sm font-medium text-gray-900">
            {(anomaly.anomalyScore * 100).toFixed(0)}%
          </span>
        </div>
      ),
    },
    {
      key: "confidence",
      header: "Confidence",
      render: (anomaly: AnomalyResult) => (
        <span className="text-sm text-gray-900">
          {(anomaly.confidence * 100).toFixed(0)}%
        </span>
      ),
    },
    {
      key: "reviewStatus",
      header: "Status",
      render: (anomaly: AnomalyResult) => (
        <StatusBadge status={anomaly.reviewStatus} />
      ),
    },
    {
      key: "amount",
      header: "Amount",
      render: (anomaly: AnomalyResult) => (
        <span className="text-sm font-medium text-gray-900">
          {anomaly.currency} {anomaly.amount?.toLocaleString() || "-"}
        </span>
      ),
    },
    {
      key: "detectedAt",
      header: "Detected At",
      render: (anomaly: AnomalyResult) => (
        <span className="text-sm text-gray-600">
          {format(new Date(anomaly.detectedAt), "MMM dd, yyyy HH:mm")}
        </span>
      ),
    },
    {
      key: "assignedTo",
      header: "Assigned To",
      render: (anomaly: AnomalyResult) => (
        <span className="text-sm text-gray-600">
          {anomaly.assignedTo || "Unassigned"}
        </span>
      ),
    },
  ];

  const navigate = useNavigate();

  const handleRowClick = (anomaly: AnomalyResult) => {
    navigate(`/narrative/${anomaly.transactionId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Anomaly Detection Results
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Monitor and review all detected anomalies across transactions
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={showExportModal}
                className="px-4 py-2 text-sm font-medium border border-gray-300 rounded-lg transition-colors flex items-center gap-2"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Export 30-Day Audit Report
              </button>
              <button className="text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                Run Detection
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-sm text-gray-600">Loading anomalies...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2">
              <svg
                className="h-5 w-5 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="text-sm text-red-800">{error}</span>
            </div>
          </div>
        )}

        {/* Content */}
        {!loading && !error && (
          <>
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="text-sm text-gray-600 mb-1">
                  Total Anomalies
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {stats.total_anomalies}
                </div>
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="text-sm text-gray-600 mb-1">Critical</div>
                <div className="text-2xl font-bold text-red-600">
                  {stats.critical}
                </div>
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="text-sm text-gray-600 mb-1">Under Review</div>
                <div className="text-2xl font-bold text-yellow-600">
                  {stats.under_review}
                </div>
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="text-sm text-gray-600 mb-1">Avg Risk Score</div>
                <div className="text-2xl font-bold text-gray-900">
                  {(stats.avg_anomaly_score * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Filters and Table */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    Anomaly Results
                  </h2>
                  <div className="flex hidden items-center gap-2">
                    <button className="px-3 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md">
                      Bulk Assign
                    </button>
                    <button className="px-3 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md">
                      Generate Report
                    </button>
                  </div>
                </div>

                <div className="flex items-center gap-3 mb-4">
                  <FilterDropdown
                    label="Severity"
                    options={severityOptions}
                    selected={filters.severity}
                    onSelect={(value) => {
                      setFilters({ ...filters, severity: value || undefined });
                      setCurrentPage(1);
                    }}
                    className="w-48"
                  />
                  <FilterDropdown
                    label="Status"
                    options={statusOptions}
                    selected={filters.review_status}
                    onSelect={(value) => {
                      setFilters({
                        ...filters,
                        review_status: value || undefined,
                      });
                      setCurrentPage(1);
                    }}
                    className="w-48"
                  />
                  <FilterDropdown
                    label="Category"
                    options={categoryOptions}
                    selected={filters.anomaly_category}
                    onSelect={(value) => {
                      setFilters({
                        ...filters,
                        anomaly_category: value || undefined,
                      });
                      setCurrentPage(1);
                    }}
                    className="w-48"
                  />
                  <button
                    onClick={() => {
                      setFilters({});
                      setCurrentPage(1);
                    }}
                    className="px-4 py-2 mt-3 text-sm font-medium "
                  >
                    Clear Filters
                  </button>
                </div>
              </div>

              {/* Table */}
              <DataTable
                data={anomalies}
                columns={columns}
                pagination={false}
                onRowClick={handleRowClick}
                emptyMessage="No anomalies found. Try adjusting your filters."
              />

              {/* Pagination */}
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                totalItems={total}
                pageSize={pageSize}
                onPageChange={setCurrentPage}
                onPageSizeChange={(size) => {
                  setPageSize(size);
                  setCurrentPage(1); // Reset to page 1 when changing page size
                }}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AnomalyListPage;
