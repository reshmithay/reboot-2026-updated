import React from "react";
import { Row, Col, Space, Button, Dropdown } from "antd";
import { DownloadOutlined, FolderOpenOutlined, MoreOutlined, EyeOutlined, FilePdfOutlined } from "@ant-design/icons";

interface AnomalyHeaderProps {
    transactionId?: string;
    onBack: () => void;
    onDownloadPDF: () => void;
    onPreviewReport: () => void;
}

export const AnomalyHeader: React.FC<AnomalyHeaderProps> = ({
    transactionId,
    onBack,
    onDownloadPDF,
    onPreviewReport
}) => {
    const downloadReportMenu = {
        items: [
            {
                key: "preview",
                label: "Preview Report",
                icon: <EyeOutlined />,
                onClick: onPreviewReport,
            },
            {
                key: "download",
                label: "Download as PDF",
                icon: <FilePdfOutlined />,
                onClick: onDownloadPDF,
            },
        ]
    };

    const moreActionsMenu = {
        items: [
            { key: "1", label: "Export to PDF" },
            { key: "2", label: "Share Report" },
            { key: "3", label: "Add to Watchlist" },
            { key: "4", label: "Create Case" },
        ]
    };

    return (
        <div style={{ marginBottom: 24 }}>
            <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
                <Col>
                    <button
                        onClick={onBack}
                        className="text-sm text-gray-600 hover:text-gray-900 mb-2 flex items-center gap-1"
                    >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        Back
                    </button>
                    <Space direction="vertical" size={0}>
                        <h1 style={{ margin: 0, fontSize: 24, fontWeight: 600 }}>Anomaly Details</h1>
                        <Space>
                            <p className="text-sm text-gray-600 mt-1">
                                Transaction ID: <code className="text-blue-600">{transactionId}</code>
                            </p>
                        </Space>
                    </Space>
                </Col>
                <Col>
                    <Space>
                        <Dropdown menu={downloadReportMenu} placement="bottomRight" trigger={['click']}>
                            <Button icon={<DownloadOutlined />} size="large">
                                Download Report
                            </Button>
                        </Dropdown>
                        <Button type="primary" icon={<FolderOpenOutlined />} size="large">
                            Open Case
                        </Button>
                        <Dropdown menu={moreActionsMenu} placement="bottomRight" trigger={['click']}>
                            <Button icon={<MoreOutlined />} size="large" />
                        </Dropdown>
                    </Space>
                </Col>
            </Row>
        </div>
    );
};
