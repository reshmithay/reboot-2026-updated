import React from "react";
import { Card, Space, Progress, Tag, Divider, Button } from "antd";
import { ExperimentOutlined } from "@ant-design/icons";

export const AIConfidence: React.FC = () => {
    return (
        <Card
            title={
                <Space>
                    <ExperimentOutlined />
                    AI Confidence
                </Space>
            }
            style={{ marginBottom: 24 }}
        >
            <Space direction="vertical" size={16} style={{ width: "100%" }}>
                <div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                        <span>Fraud Probability</span>
                        <span style={{ fontWeight: 600, color: "#ff4d4f" }}>84%</span>
                    </div>
                    <Progress percent={84} strokeColor="#ff4d4f" showInfo={false} />
                </div>
                <div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                        <span>Model Confidence</span>
                        <span style={{ fontWeight: 600, color: "#52c41a" }}>95%</span>
                    </div>
                    <Progress percent={95} strokeColor="#52c41a" showInfo={false} />
                </div>
                <div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                        <span>False Positive Probability</span>
                        <span style={{ fontWeight: 600, color: "#faad14" }}>8%</span>
                    </div>
                    <Progress percent={8} strokeColor="#faad14" showInfo={false} />
                </div>
                <div>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                        <span>Explainability Score</span>
                        <Tag color="green">High</Tag>
                    </div>
                </div>
            </Space>
            <Divider />
            <Button type="link" block style={{ padding: 0 }}>
                View Model Explanation →
            </Button>
        </Card>
    );
};
