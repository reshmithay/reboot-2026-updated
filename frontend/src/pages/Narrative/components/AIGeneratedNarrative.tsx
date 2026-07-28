import React from "react";
import { Card, Space, Button, Tabs, Table, Tag } from "antd";
import {
    ExperimentOutlined,
    SafetyOutlined,
    UserOutlined,
    TeamOutlined,
    LineChartOutlined,
    SoundOutlined,
    PauseCircleOutlined,
    RiseOutlined,
    FallOutlined,
} from "@ant-design/icons";

interface ShapContributor {
    feature: string;
    actual_value: number;
    shap_contribution: number;
    direction: string;
}

interface AIGeneratedNarrativeProps {
    selectedPersona: string;
    isPlaying: boolean;
    narratives: Record<string, { title: string; content: string }>;
    onPersonaChange: (value: string) => void;
    onPlayPause: () => void;
    shapContributors?: ShapContributor[];
    predictionLabel?: string;
    modelUsed?: string;
}

export const AIGeneratedNarrative: React.FC<AIGeneratedNarrativeProps> = ({
    selectedPersona,
    isPlaying,
    narratives,
    onPersonaChange,
    onPlayPause,
    shapContributors,
    predictionLabel,
    modelUsed,
}) => {
    const columns = [
        {
            title: 'Feature',
            dataIndex: 'feature',
            key: 'feature',
            width: '40%',
        },
        {
            title: 'Value',
            dataIndex: 'actual_value',
            key: 'actual_value',
            width: '20%',
            render: (value: number) => value.toFixed(2),
        },
        {
            title: 'SHAP Impact',
            dataIndex: 'shap_contribution',
            key: 'shap_contribution',
            width: '20%',
            render: (value: number) => (
                <Tag color={value > 0 ? 'red' : 'green'}>
                    {value > 0 ? '+' : ''}{value.toFixed(4)}
                </Tag>
            ),
        },
        {
            title: 'Direction',
            dataIndex: 'direction',
            key: 'direction',
            width: '20%',
            render: (direction: string) => (
                <Space>
                    {direction === 'increased' ? (
                        <>
                            <RiseOutlined style={{ color: '#ff4d4f' }} />
                            <span style={{ color: '#ff4d4f' }}>Risk ↑</span>
                        </>
                    ) : (
                        <>
                            <FallOutlined style={{ color: '#52c41a' }} />
                            <span style={{ color: '#52c41a' }}>Risk ↓</span>
                        </>
                    )}
                </Space>
            ),
        },
    ];

    return (
        <Card
            title={
                <Space>
                    <ExperimentOutlined />
                    AI Generated Narrative {modelUsed && <Tag color="blue">{modelUsed}</Tag>}
                    {predictionLabel && <Tag color="red">{predictionLabel}</Tag>}
                </Space>
            }
            extra={
                <Button
                    type={isPlaying ? "primary" : "default"}
                    icon={isPlaying ? <PauseCircleOutlined /> : <SoundOutlined />}
                    onClick={onPlayPause}
                >
                    {isPlaying ? "Stop Audio" : "Play Audio"}
                </Button>
            }
            style={{ marginBottom: 24 }}
        >
            <Tabs
                activeKey={selectedPersona}
                onChange={onPersonaChange}
                items={[
                    {
                        key: "fraud-analyst",
                        label: (
                            <Space>
                                <ExperimentOutlined />
                                Fraud Analyst
                            </Space>
                        ),
                        children: (
                            <>
                                <div style={{ fontSize: 14, lineHeight: 1.8, color: "#595959", whiteSpace: "pre-line", padding: "16px 0" }}>
                                    {narratives["fraud-analyst"].content}
                                </div>
                                {shapContributors && shapContributors.length > 0 && (
                                    <div style={{ marginTop: 24 }}>
                                        <h4 style={{ marginBottom: 16 }}>Top Risk Factors (SHAP Analysis)</h4>
                                        <Table
                                            dataSource={shapContributors}
                                            columns={columns}
                                            pagination={false}
                                            size="small"
                                            rowKey="feature"
                                        />
                                    </div>
                                )}
                            </>
                        ),
                    },
                    {
                        key: "compliance-officer",
                        label: (
                            <Space>
                                <SafetyOutlined />
                                Compliance Officer
                            </Space>
                        ),
                        children: (
                            <div style={{ fontSize: 14, lineHeight: 1.8, color: "#595959", whiteSpace: "pre-line", padding: "16px 0" }}>
                                {narratives["compliance-officer"].content}
                            </div>
                        ),
                    },
                    {
                        key: "relationship-manager",
                        label: (
                            <Space>
                                <UserOutlined />
                                Relationship Manager
                            </Space>
                        ),
                        children: (
                            <div style={{ fontSize: 14, lineHeight: 1.8, color: "#595959", whiteSpace: "pre-line", padding: "16px 0" }}>
                                {narratives["relationship-manager"].content}
                            </div>
                        ),
                    },
                    {
                        key: "auditor",
                        label: (
                            <Space>
                                <LineChartOutlined />
                                Auditor
                            </Space>
                        ),
                        children: (
                            <div style={{ fontSize: 14, lineHeight: 1.8, color: "#595959", whiteSpace: "pre-line", padding: "16px 0" }}>
                                {narratives["auditor"]?.content || narratives["fraud-analyst"].content}
                            </div>
                        ),
                    },
                    {
                        key: "regulator",
                        label: (
                            <Space>
                                <SafetyOutlined />
                                FCA / Regulator
                            </Space>
                        ),
                        children: (
                            <div style={{ fontSize: 14, lineHeight: 1.8, color: "#595959", whiteSpace: "pre-line", padding: "16px 0" }}>
                                {narratives["regulator"]?.content || narratives["fraud-analyst"].content}
                            </div>
                        ),
                    },
                    {
                        key: "executive-summary",
                        label: (
                            <Space>
                                <TeamOutlined />
                                Operations Team
                            </Space>
                        ),
                        children: (
                            <div style={{ fontSize: 14, lineHeight: 1.8, color: "#595959", whiteSpace: "pre-line", padding: "16px 0" }}>
                                {narratives["operations-team"].content}
                            </div>
                        ),
                    },
                    {
                        key: "executive-summary",
                        label: (
                            <Space>
                                <LineChartOutlined />
                                Executive Summary
                            </Space>
                        ),
                        children: (
                            <div style={{ fontSize: 14, lineHeight: 1.8, color: "#595959", whiteSpace: "pre-line", padding: "16px 0" }}>
                                {narratives["executive-summary"].content}
                            </div>
                        ),
                    },
                ]}
            />
        </Card>
    );
};
