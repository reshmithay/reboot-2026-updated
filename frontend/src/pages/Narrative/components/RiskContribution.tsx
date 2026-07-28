import React from "react";
import { Card, Space, Progress } from "antd";

interface RiskFactor {
    factor: string;
    percentage: number;
    color: string;
}

interface RiskContributionProps {
    factors: RiskFactor[];
}

export const RiskContribution: React.FC<RiskContributionProps> = ({ factors }) => {
    return (
        <Card title="Risk Contribution" style={{ marginBottom: 24 }}>
            <div style={{ textAlign: "center", marginBottom: 16 }}>
                <Progress
                    type="circle"
                    percent={100}
                    strokeColor={{
                        "0%": "#ff4d4f",
                        "50%": "#faad14",
                        "100%": "#52c41a",
                    }}
                    format={() => (
                        <div>
                            <div style={{ fontSize: 24, fontWeight: 700 }}>100%</div>
                            <div style={{ fontSize: 12, color: "#666" }}>Total Risk</div>
                        </div>
                    )}
                    width={120}
                />
            </div>
            <Space direction="vertical" size={8} style={{ width: "100%" }}>
                {factors.map((item, idx) => (
                    <div key={idx}>
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                            <Space>
                                <div
                                    style={{
                                        width: 8,
                                        height: 8,
                                        borderRadius: "50%",
                                        backgroundColor: item.color,
                                    }}
                                />
                                <span style={{ fontSize: 13 }}>{item.factor}</span>
                            </Space>
                            <span style={{ fontWeight: 600, fontSize: 13 }}>{item.percentage}%</span>
                        </div>
                    </div>
                ))}
            </Space>
        </Card>
    );
};
