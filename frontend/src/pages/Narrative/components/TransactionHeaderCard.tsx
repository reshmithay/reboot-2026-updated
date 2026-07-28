import React from "react";
import { Card, Row, Col, Space, Tag, Progress } from "antd";
import { format } from "date-fns";
import { AnomalyResult, Transaction } from "@/types";

interface TransactionHeaderCardProps {
    anomaly: AnomalyResult;
    transaction: Transaction | null;
}

export const TransactionHeaderCard: React.FC<TransactionHeaderCardProps> = ({
    anomaly,
    transaction
}) => {
    const riskScore = anomaly?.anomalyScore ? Math.round(anomaly.anomalyScore * 100) : 0;

    return (
        <Card style={{ marginBottom: 24 }}>
            <Row gutter={[24, 24]}>
                <Col span={18}>
                    <Row gutter={[32, 16]}>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Transaction ID</span>
                                <span style={{ fontSize: 18, fontWeight: 600 }}>
                                    {transaction?.transaction_id || anomaly?.transactionId || "N/A"}
                                </span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Date & Time</span>
                                <span style={{ fontSize: 16 }}>
                                    {transaction?.transaction_timestamp 
                                        ? format(new Date(transaction.transaction_timestamp), "dd MMM yyyy, hh:mm a") 
                                        : "N/A"}
                                </span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Amount</span>
                                <span style={{ fontSize: 18, fontWeight: 600, color: "#ff4d4f" }}>
                                    {transaction 
                                        ? `${transaction.currency || "INR"} ${transaction.amount?.toLocaleString() || "0"}` 
                                        : "N/A"}
                                </span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Client Name</span>
                                <span style={{ fontSize: 16 }}>{transaction?.client_name || "N/A"}</span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Source Account</span>
                                <span style={{ fontSize: 16 }}>{transaction?.from_account || "N/A"}</span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Destination Account</span>
                                <span style={{ fontSize: 16 }}>{transaction?.to_account || "N/A"}</span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Client ID</span>
                                <span style={{ fontSize: 16 }}>
                                    {transaction?.client_id || anomaly?.clientId || "N/A"}
                                </span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Channel</span>
                                <span style={{ fontSize: 16 }}>
                                    {transaction?.transaction_category || transaction?.blockchain_network || "N/A"}
                                </span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Status</span>
                                <Tag color="orange">
                                    {anomaly?.reviewStatus || transaction?.transaction_status || "N/A"}
                                </Tag>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Anomaly ID</span>
                                <span style={{ fontSize: 16 }}>{anomaly?.anomalyId}</span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Category</span>
                                <span style={{ fontSize: 16 }}>{anomaly?.anomalyCategory}</span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Confidence</span>
                                <span style={{ fontSize: 16 }}>{anomaly?.confidence}</span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Model</span>
                                <span style={{ fontSize: 16 }}>
                                    {anomaly?.modelName || "N/A"} {anomaly?.modelVersion ? `v${anomaly?.modelVersion}` : ""}
                                </span>
                            </Space>
                        </Col>
                        <Col span={8}>
                            <Space direction="vertical" size={0}>
                                <span style={{ color: "#666", fontSize: 12 }}>Detected At</span>
                                <span style={{ fontSize: 16 }}>
                                    {anomaly?.detectedAt 
                                        ? format(new Date(anomaly.detectedAt), "MMM dd, yyyy HH:mm:ss") 
                                        : "N/A"}
                                </span>
                            </Space>
                        </Col>
                    </Row>
                </Col>
                <Col span={6}>
                    <div style={{ textAlign: "center" }}>
                        <div style={{ marginBottom: 8, color: "#666", fontSize: 14 }}>Risk Score</div>
                        <Progress
                            type="circle"
                            percent={riskScore}
                            strokeColor={{
                                "0%": "#ff4d4f",
                                "100%": "#cf1322",
                            }}
                            format={(percent) => (
                                <div>
                                    <div style={{ fontSize: 32, fontWeight: 700, color: "#ff4d4f" }}>{percent}</div>
                                    <div style={{ fontSize: 12, color: "#666" }}>/100</div>
                                </div>
                            )}
                            width={140}
                        />
                        <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
                            {anomaly?.severity || "Unknown"} Risk
                        </div>
                        <div style={{ fontSize: 12, fontWeight: 600 }}>
                            {anomaly?.anomalyCategory || "Unknown"}
                        </div>
                    </div>
                </Col>
            </Row>
        </Card>
    );
};
