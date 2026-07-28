import React from "react";
import { Card, Space, Alert } from "antd";
import { WarningOutlined } from "@ant-design/icons";

export interface RiskIndicator {
    id: string;
    icon: React.ReactNode;
    label: string;
    description: string;
    severity: "high" | "medium" | "low";
}

interface KeyRiskIndicatorsProps {
    indicators: RiskIndicator[];
}

export const KeyRiskIndicators: React.FC<KeyRiskIndicatorsProps> = ({ indicators }) => {
    return (
        <Card
            title={
                <Space>
                    <WarningOutlined />
                    Key Risk Indicators
                </Space>
            }
            style={{ marginBottom: 24 }}
        >
            <Space direction="vertical" size={12} style={{ width: "100%" }}>
                {indicators.map((indicator) => (
                    <Alert
                        key={indicator.id}
                        message={
                            <Space>
                                {indicator.icon}
                                {indicator.label}
                            </Space>
                        }
                        description={indicator.description}
                        type={indicator.severity === "high" ? "error" : "warning"}
                        showIcon={false}
                    />
                ))}
            </Space>
        </Card>
    );
};
