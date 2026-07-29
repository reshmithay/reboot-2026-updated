import React from "react";
import { Card, Descriptions, Table, Tag, Divider, Space, Progress } from "antd";
import { format } from "date-fns";
import { AnomalyResult, Transaction } from "@/types";
import type { RiskIndicator, RecommendedAction, TimelineEvent } from "./index";

interface ReportPreviewProps {
  anomaly: AnomalyResult;
  transaction: Transaction | null;
  narratives: Record<string, { title: string; content: string }>;
  riskIndicators: RiskIndicator[];
  recommendedActions: RecommendedAction[];
  timeline: TimelineEvent[];
  riskContribution: Array<{
    factor: string;
    percentage: number;
    color: string;
  }>;
}

export const ReportPreview: React.FC<ReportPreviewProps> = ({
  anomaly,
  transaction,
  narratives,
  recommendedActions,
  timeline,
  riskContribution,
}) => {
  const riskScore = anomaly?.anomalyScore
    ? Math.round(anomaly.anomalyScore * 100)
    : 0;
  const transactionData = {
    id: transaction?.transaction_id || anomaly?.transactionId || "N/A",
    date: transaction?.transaction_timestamp
      ? format(
          new Date(transaction.transaction_timestamp),
          "dd MMM yyyy, hh:mm a",
        )
      : "N/A",
    amount: transaction
      ? `${transaction.currency || "INR"} ${transaction.amount?.toLocaleString() || "0"}`
      : "N/A",
  };

  return (
    <div style={{ maxHeight: "70vh", overflowY: "auto", padding: "20px" }}>
      {/* Report Header */}
      <div
        style={{
          background:
            "linear-gradient(135deg, rgb(24 125 57) 0%, rgb(30, 64, 175) 100%)",
          color: "white",
          padding: "30px",
          borderRadius: "8px 8px 0 0",
          marginBottom: "24px",
        }}
      >
        <h1
          style={{
            color: "white",
            margin: 0,
            fontSize: "24px",
            fontWeight: "bold",
            textAlign: "center",
          }}
        >
          BLOCKCHAIN ANOMALY INTELLIGENCE REPORT
        </h1>
        <p
          style={{
            color: "rgba(255,255,255,0.9)",
            textAlign: "center",
            margin: "8px 0 0 0",
            fontSize: "12px",
          }}
        >
          Confidential - For Internal Use Only
        </p>
      </div>

      {/* Report Metadata */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Descriptions column={2} size="small">
          <Descriptions.Item label="Transaction ID">
            <strong>{transactionData.id}</strong>
          </Descriptions.Item>
          <Descriptions.Item label="Report Generated">
            {new Date().toLocaleString()}
          </Descriptions.Item>
          <Descriptions.Item label="Risk Score" span={2}>
            <Space>
              <Progress
                type="circle"
                percent={riskScore}
                width={50}
                strokeColor={
                  riskScore > 70
                    ? "#ff4d4f"
                    : riskScore > 40
                      ? "#faad14"
                      : "#52c41a"
                }
              />
              <Tag color="red" style={{ fontSize: "14px" }}>
                {riskScore}/100 - Very High Risk
              </Tag>
            </Space>
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Transaction Details */}
      <Card
        title="TRANSACTION DETAILS"
        size="small"
        style={{ marginBottom: 16 }}
      >
        <Descriptions column={2} size="small" bordered>
          <Descriptions.Item label="Date & Time">
            {transactionData.date}
          </Descriptions.Item>
          <Descriptions.Item label="Amount">
            {transactionData.amount}
          </Descriptions.Item>
          <Descriptions.Item label="Channel">
            {transaction?.transaction_category || "N/A"}
          </Descriptions.Item>
          <Descriptions.Item label="Status">
            <Tag color="orange">{anomaly?.reviewStatus || "Under Review"}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Transaction Type">
            {transaction?.transaction_type || "N/A"}
          </Descriptions.Item>
          <Descriptions.Item label="Customer Name">
            {transaction?.client_name || "N/A"}
          </Descriptions.Item>
          <Descriptions.Item label="Customer ID">
            {transaction?.client_id || anomaly?.clientId || "N/A"}
          </Descriptions.Item>
          <Descriptions.Item label="Source Account">
            {transaction?.from_account || "N/A"}
          </Descriptions.Item>
          <Descriptions.Item label="Destination Account" span={2}>
            {transaction?.to_account || "N/A"}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* AI-Generated Narrative */}
      <Card
        title="AI-GENERATED NARRATIVE (Fraud Analyst)"
        size="small"
        style={{ marginBottom: 16 }}
      >
        <div
          style={{
            fontSize: "13px",
            lineHeight: 1.8,
            color: "#595959",
            whiteSpace: "pre-line",
            background: "#fafafa",
            padding: "16px",
            borderRadius: "4px",
          }}
        >
          {narratives["fraud-analyst"]?.content}
        </div>
      </Card>
      {/* Recommended Actions */}
      <Card
        title="RECOMMENDED ACTIONS"
        size="small"
        style={{ marginBottom: 16 }}
      >
        {recommendedActions.map((action) => (
          <div key={action.priority} style={{ marginBottom: 16 }}>
            <h4
              style={{
                color:
                  action.priority === "immediate"
                    ? "#cf1322"
                    : action.priority === "within-1-hour"
                      ? "#d46b08"
                      : "#389e0d",
                marginBottom: 8,
              }}
            >
              {action.title}
            </h4>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {action.actions.map((item, idx) => (
                <li key={idx} style={{ fontSize: "13px", marginBottom: 4 }}>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </Card>

      {/* Investigation Timeline */}
      <Card
        title="INVESTIGATION TIMELINE"
        size="small"
        style={{ marginBottom: 16 }}
      >
        <Space direction="vertical" style={{ width: "100%" }} size="small">
          {timeline.map((event, idx) => (
            <div
              key={idx}
              style={{
                padding: "12px",
                borderLeft: `4px solid ${event.type === "error" ? "#ff4d4f" : event.type === "warning" ? "#faad14" : "#1890ff"}`,
                background: "#fafafa",
                borderRadius: "4px",
              }}
            >
              <div style={{ fontWeight: 600, marginBottom: 4 }}>
                [{event.time}] {event.title}
              </div>
              <div style={{ fontSize: "12px", color: "#595959" }}>
                {event.description}
              </div>
            </div>
          ))}
        </Space>
      </Card>

      {/* AI Confidence Metrics */}
      <Card
        title="AI CONFIDENCE METRICS"
        size="small"
        style={{ marginBottom: 16 }}
      >
        <Table
          size="small"
          pagination={false}
          dataSource={[
            { key: "1", metric: "Fraud Probability", value: "84%" },
            { key: "2", metric: "Model Confidence", value: "95%" },
            { key: "3", metric: "False Positive Probability", value: "8%" },
            { key: "4", metric: "Explainability Score", value: "High" },
          ]}
          columns={[
            { title: "Metric", dataIndex: "metric", key: "metric" },
            {
              title: "Value",
              dataIndex: "value",
              key: "value",
              align: "right" as const,
            },
          ]}
        />
      </Card>

      {/* Risk Contribution */}
      <Card
        title="RISK CONTRIBUTION BREAKDOWN"
        size="small"
        style={{ marginBottom: 16 }}
      >
        <Table
          size="small"
          pagination={false}
          dataSource={riskContribution.map((item, idx) => ({
            key: idx,
            factor: item.factor,
            contribution: `${item.percentage}%`,
          }))}
          columns={[
            { title: "Risk Factor", dataIndex: "factor", key: "factor" },
            {
              title: "Contribution",
              dataIndex: "contribution",
              key: "contribution",
              align: "right" as const,
            },
          ]}
        />
      </Card>

      <Divider />

      {/* Footer */}
      <div style={{ fontSize: 11, color: "#999", textAlign: "center" }}>
        <p style={{ margin: "4px 0" }}>
          <strong>COMPLIANCE NOTICE</strong>
        </p>
        <p style={{ margin: "4px 0" }}>
          This report is generated by Blockchain Anomaly AI for compliance and
          risk assessment purposes.
        </p>
        <p style={{ margin: "4px 0" }}>
          All findings should be reviewed by qualified personnel before taking
          action.
        </p>
        <p style={{ margin: "4px 0" }}>This is a confidential document.</p>
        <p style={{ margin: "8px 0 0 0", fontSize: 10 }}>
          Report ID: {transactionData.id}-{Date.now()} | Generated:{" "}
          {new Date().toLocaleString()}
        </p>
      </div>
    </div>
  );
};
