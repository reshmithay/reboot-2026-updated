import React from "react";
import { Card, Row, Col, Space } from "antd";
import { ThunderboltOutlined, WarningOutlined, ClockCircleOutlined, SafetyOutlined } from "@ant-design/icons";

export interface RecommendedAction {
    priority: "immediate" | "within-1-hour" | "long-term";
    title: string;
    actions: string[];
}

interface RecommendedActionsProps {
    actions: RecommendedAction[];
}

const getPriorityColor = (priority: string) => {
    switch (priority) {
        case "immediate": return "#ff4d4f";
        case "within-1-hour": return "#faad14";
        case "long-term": return "#52c41a";
        default: return "#d9d9d9";
    }
};

const getPriorityIcon = (priority: string) => {
    switch (priority) {
        case "immediate": return <WarningOutlined />;
        case "within-1-hour": return <ClockCircleOutlined />;
        case "long-term": return <SafetyOutlined />;
        default: return null;
    }
};

export const RecommendedActions: React.FC<RecommendedActionsProps> = ({ actions }) => {
    return (
        <Card
            title={
                <Space>
                    <ThunderboltOutlined />
                    Recommended Next Best Actions
                </Space>
            }
            style={{ marginBottom: 24 }}
        >
            <Row gutter={16}>
                {actions.map((action) => (
                    <Col span={8} key={action.priority}>
                        <div
                            style={{
                                padding: 16,
                                border: `2px solid ${getPriorityColor(action.priority)}`,
                                borderRadius: 8,
                                height: "100%",
                            }}
                        >
                            <div style={{ marginBottom: 12 }}>
                                <Space>
                                    {getPriorityIcon(action.priority)}
                                    <span style={{ fontWeight: 600, color: getPriorityColor(action.priority) }}>
                                        {action.title}
                                    </span>
                                </Space>
                            </div>
                            <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13 }}>
                                {action.actions.map((item, idx) => (
                                    <li key={idx} style={{ marginBottom: 6 }}>
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </Col>
                ))}
            </Row>
        </Card>
    );
};
