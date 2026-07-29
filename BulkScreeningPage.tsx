import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Button,
  Result,
  Spin,
  Typography,
  Upload,
  Alert,
  Table,
  Tag,
} from "antd";
import {
  CloudUploadOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  InboxOutlined,
} from "@ant-design/icons";
import type { UploadFile } from "antd/es/upload/interface";
import anomalyService, { BulkDetectResponse } from "../../services/anomaly/anomalyService";

const { Title, Text, Paragraph } = Typography;
const { Dragger } = Upload;

type PageState = "idle" | "loading" | "success" | "error";

const BulkScreeningPage: React.FC = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [pageState, setPageState] = useState<PageState>("idle");
  const [summary, setSummary] = useState<BulkDetectResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>("");

  // ── Upload handlers ──────────────────────────────────────────────────────────

  const handleBeforeUpload = (f: File) => {
    setFile(f);
    setFileList([
      {
        uid: "-1",
        name: f.name,
        status: "done",
        size: f.size,
        type: f.type,
      },
    ]);
    // Prevent automatic upload
    return false;
  };

  const handleRemove = () => {
    setFile(null);
    setFileList([]);
  };

  // ── Submission ───────────────────────────────────────────────────────────────

  const handleSubmit = async () => {
    if (!file) return;

    setPageState("loading");
    setErrorMsg("");

    try {
      const result = await anomalyService.bulkDetect(file);
      setSummary(result);
      setPageState("success");
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
            "Bulk detection failed. Please try again.";
      setErrorMsg(message);
      setPageState("error");
    }
  };

  // ── Render helpers ───────────────────────────────────────────────────────────

  const renderIdle = () => (
    <div style={{ maxWidth: 640, margin: "0 auto" }}>
      <Title level={3} style={{ color: "#003366", marginBottom: 4 }}>
        Bulk Transaction Screening
      </Title>
      <Paragraph type="secondary" style={{ marginBottom: 24 }}>
        Upload a CSV file containing transaction hashes. The system will run anomaly
        detection on each transaction and store the results.
        <br />
        <Text type="secondary" style={{ fontSize: 12 }}>
          CSV must have a <code>transaction_hash</code> header column. Maximum 100 rows per upload.
        </Text>
      </Paragraph>

      <Dragger
        accept=".csv"
        fileList={fileList}
        beforeUpload={handleBeforeUpload}
        onRemove={handleRemove}
        maxCount={1}
        style={{ padding: "24px 0", borderRadius: 8 }}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined style={{ color: "#2563eb", fontSize: 40 }} />
        </p>
        <p className="ant-upload-text">Click or drag a CSV file here</p>
        <p className="ant-upload-hint">
          Required column: <code>transaction_hash</code>
        </p>
      </Dragger>

      {file && (
        <div style={{ marginTop: 12, color: "#595959" }}>
          Selected: <strong>{file.name}</strong> ({(file.size / 1024).toFixed(1)} KB)
        </div>
      )}

      <Button
        type="primary"
        size="large"
        icon={<CloudUploadOutlined />}
        onClick={handleSubmit}
        disabled={!file}
        style={{ marginTop: 24, width: "100%", height: 44 }}
      >
        Upload &amp; Run Detection
      </Button>

      <div style={{ marginTop: 24, background: "#f6f8fa", borderRadius: 8, padding: 16 }}>
        <Text strong>Expected CSV format:</Text>
        <pre
          style={{
            marginTop: 8,
            background: "#fff",
            border: "1px solid #e0e0e0",
            borderRadius: 6,
            padding: "10px 14px",
            fontSize: 13,
            overflowX: "auto",
          }}
        >
          {`transaction_hash\n0xabc123...\n0xdef456...\n0x789ghi...`}
        </pre>
      </div>
    </div>
  );

  const renderLoading = () => (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: 320,
        gap: 24,
      }}
    >
      <Spin size="large" />
      <Title level={4} style={{ color: "#003366", margin: 0 }}>
        Running anomaly detection…
      </Title>
      <Paragraph type="secondary" style={{ textAlign: "center", maxWidth: 420 }}>
        Processing each transaction hash in your CSV. This may take a moment depending on
        the number of rows. Please keep this page open.
      </Paragraph>
    </div>
  );

  const renderSuccess = () => {
    if (!summary) return null;

    const errorRows = summary.errors.map((e, i) => ({ key: i, ...e }));

    return (
      <div style={{ maxWidth: 700, margin: "0 auto" }}>
        <Result
          status="success"
          icon={<CheckCircleOutlined style={{ color: "#10a870" }} />}
          title="Bulk Screening Completed"
          subTitle={`${summary.total} transaction(s) processed`}
          extra={[
            <Button
              type="primary"
              key="view"
              onClick={() => navigate("/anomalies")}
              style={{ minWidth: 160 }}
            >
              View Anomalies
            </Button>,
            <Button key="again" onClick={() => { setPageState("idle"); setFile(null); setFileList([]); setSummary(null); }}>
              Screen Another File
            </Button>,
          ]}
        />

        {/* Summary cards */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: 16,
            marginBottom: 24,
          }}
        >
          {[
            { label: "Total Processed", value: summary.total, color: "#2563eb" },
            { label: "Anomalies Detected", value: summary.anomalies_found, color: "#db0f30", icon: <WarningOutlined /> },
            { label: "Clean Transactions", value: summary.clean, color: "#10a870" },
          ].map(({ label, value, color, icon }) => (
            <div
              key={label}
              style={{
                background: "#fff",
                border: `1px solid ${color}33`,
                borderRadius: 10,
                padding: "18px 20px",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: 28, fontWeight: 700, color }}>
                {icon && <span style={{ marginRight: 6 }}>{icon}</span>}
                {value}
              </div>
              <div style={{ fontSize: 13, color: "#595959", marginTop: 4 }}>{label}</div>
            </div>
          ))}
        </div>

        {/* Errors table */}
        {summary.error_count > 0 && (
          <>
            <Alert
              type="warning"
              showIcon
              message={`${summary.error_count} transaction(s) could not be processed`}
              style={{ marginBottom: 12 }}
            />
            <Table
              size="small"
              pagination={false}
              dataSource={errorRows}
              columns={[
                { title: "Transaction Hash", dataIndex: "transaction_hash", key: "hash", ellipsis: true },
                { title: "Error", dataIndex: "error", key: "error", ellipsis: true },
              ]}
            />
          </>
        )}
      </div>
    );
  };

  const renderError = () => (
    <div style={{ maxWidth: 540, margin: "0 auto" }}>
      <Result
        status="error"
        title="Detection Failed"
        subTitle={errorMsg || "An unexpected error occurred."}
        extra={[
          <Button type="primary" key="retry" onClick={() => setPageState("idle")}>
            Try Again
          </Button>,
        ]}
      />
    </div>
  );

  // ── Main render ──────────────────────────────────────────────────────────────

  return (
    <div
      style={{
        minHeight: "calc(100vh - 64px)",
        padding: "40px 32px",
        background: "#f5f7fa",
      }}
    >
      <div
        style={{
          background: "#fff",
          borderRadius: 12,
          padding: "40px 48px",
          boxShadow: "0 2px 12px rgba(0,0,0,0.07)",
          minHeight: 400,
        }}
      >
        {pageState === "idle" && renderIdle()}
        {pageState === "loading" && renderLoading()}
        {pageState === "success" && renderSuccess()}
        {pageState === "error" && renderError()}
      </div>
    </div>
  );
};

export default BulkScreeningPage;
