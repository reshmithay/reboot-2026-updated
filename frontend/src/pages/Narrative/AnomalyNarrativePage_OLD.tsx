import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import { Row, Col, Button, Modal, message, Descriptions, Tag, Card, Space, Timeline } from "antd";
import { FilePdfOutlined, EyeOutlined, DownloadOutlined } from "@ant-design/icons";
import { format } from "date-fns";

// Hooks
import { useAnomalyData, useNarrativeAudio } from "./hooks";

// Components
import {
    AnomalyHeader,
    TransactionHeaderCard,
    AIGeneratedNarrative,
    AnomalyReasonsCard,
    KeyRiskIndicators,
    RecommendedActions,
    TransactionSnapshot,
    AIConfidence,
    RiskContribution,
    InvestigationTimeline,
} from "./components";

// Constants
import {
    LANGUAGES,
    RISK_INDICATORS,
    RISK_CONTRIBUTION,
    INVESTIGATION_TIMELINE,
    RECOMMENDED_ACTIONS,
    NARRATIVE_TRANSLATIONS,
} from "./constants";


const AnomalyNarrativePage: React.FC = () => {
    const navigate = useNavigate();
    const reportRef = useRef<HTMLDivElement>(null);

    // Data fetching
    const { anomaly, transaction, loading, error, transactionId } = useAnomalyData();

    // UI state
    const [selectedPersona, setSelectedPersona] = useState<string>("fraud-analyst");
    const [selectedLanguage, setSelectedLanguage] = useState<string>("en");
    const [isReportModalVisible, setIsReportModalVisible] = useState(false);

    // Narrative translations
    const aiNarratives = NARRATIVE_TRANSLATIONS[selectedLanguage] || NARRATIVE_TRANSLATIONS.en;

    // Audio playback
    const { isPlaying, handlePlayNarrative } = useNarrativeAudio(
        LANGUAGES,
        aiNarratives,
        selectedLanguage,
        selectedPersona
    );

    // Computed values from API data
    const transactionData = {
        id: transaction?.transaction_id || anomaly?.transactionId || "N/A",
        date: transaction?.transaction_timestamp
            ? format(new Date(transaction.transaction_timestamp), "dd MMM yyyy, hh:mm a")
            : "N/A",
        amount: transaction
            ? `${transaction.currency || "INR"} ${transaction.amount?.toLocaleString() || "0"}`
            : "N/A",
        channel: transaction?.transaction_category || "N/A",
        status: anomaly?.reviewStatus || "Under Review",
        riskScore: anomaly?.anomalyScore ? Math.round(anomaly.anomalyScore * 100) : 0,
        customerName: transaction?.client_name || "N/A",
        customerId: transaction?.client_id || anomaly?.clientId || "N/A",
        sourceAccount: transaction?.from_account || "N/A",
        destinationAccount: transaction?.to_account || "N/A",
        location: "N/A",
        transactionType: transaction?.transaction_type || "N/A",
        averageTransaction: "N/A",
        velocityIncrease: "N/A",
        beneficiaryAddedOn: "N/A",
        timeSinceBeneficiary: "N/A",
        device: "N/A",
        ipAddress: "N/A",
        anomalyCategory: anomaly?.anomalyCategory || "Unknown",
    };

    const handlePreviewReport = () => {
        setIsReportModalVisible(true);
    };


    const handleDownloadPDF = () => {
        message.loading({ content: 'Generating PDF report...', key: 'pdf-download' });

        setTimeout(() => {
            try {
                const doc = new jsPDF();
                let yPos = 20;
                const pageWidth = doc.internal.pageSize.getWidth();
                const margin = 20;
                const maxWidth = pageWidth - 2 * margin;

                // Helper function to add text with word wrap
                const addText = (text: string, fontSize: number = 10, isBold: boolean = false, color: number[] = [0, 0, 0]) => {
                    doc.setFontSize(fontSize);
                    doc.setFont("helvetica", isBold ? "bold" : "normal");
                    doc.setTextColor(color[0], color[1], color[2]);
                    const lines = doc.splitTextToSize(text, maxWidth);

                    lines.forEach((line: string) => {
                        if (yPos > 270) {
                            doc.addPage();
                            yPos = 20;
                        }
                        doc.text(line, margin, yPos);
                        yPos += fontSize * 0.5;
                    });
                    yPos += 3;
                };

                const addSection = (title: string) => {
                    yPos += 5;
                    doc.setFillColor(240, 240, 240);
                    doc.rect(margin, yPos - 5, maxWidth, 8, 'F');
                    addText(title, 12, true);
                    yPos += 2;
                };

                // Title
                doc.setFillColor(37, 99, 235);
                doc.rect(0, 0, pageWidth, 40, 'F');
                doc.setTextColor(255, 255, 255);
                doc.setFontSize(18);
                doc.setFont("helvetica", "bold");
                doc.text("BLOCKCHAIN ANOMALY INTELLIGENCE REPORT", pageWidth / 2, 20, { align: "center" });
                doc.setFontSize(10);
                doc.text("Confidential - For Internal Use Only", pageWidth / 2, 30, { align: "center" });

                yPos = 50;
                doc.setTextColor(0, 0, 0);

                // Report Header
                addText(`Transaction ID: ${transaction?.id}`, 11, true);
                addText(`Report Generated: ${new Date().toLocaleString()}`, 10);
                addText(`Risk Score: ${transactionData.riskScore}/100 - Very High Risk`, 11, true, [220, 38, 38]);

                // Transaction Details
                addSection("TRANSACTION DETAILS");
                autoTable(doc, {
                    startY: yPos,
                    head: [['Field', 'Value']],
                    body: [
                        ['Date & Time', transactionData.date],
                        ['Amount', transactionData.amount],
                        ['Channel', transactionData.channel],
                        ['Status', transactionData.status],
                        ['Transaction Type', transactionData.transactionType],
                        ['Customer Name', transactionData.customerName],
                        ['Customer ID', transactionData.customerId],
                        ['Source Account', transactionData.sourceAccount],
                        ['Destination Account', transactionData.destinationAccount],
                        ['Location', transactionData.location],
                        ['Device', transactionData.device],
                        ['IP Address', transactionData.ipAddress],
                    ],
                    theme: 'grid',
                    headStyles: { fillColor: [37, 99, 235], textColor: 255 },
                    margin: { left: margin, right: margin },
                });
                yPos = (doc as any).lastAutoTable.finalY + 10;

                // AI-Generated Narrative
                addSection("AI-GENERATED NARRATIVE (Fraud Analyst)");
                addText(aiNarratives["fraud-analyst"].content, 10);

                // Key Risk Indicators
                addSection("KEY RISK INDICATORS");
                riskIndicators.forEach((indicator, idx) => {
                    const severityColor = indicator.severity === 'high' ? [220, 38, 38] : [245, 158, 11];
                    addText(`${idx + 1}. [${indicator.severity.toUpperCase()}] ${indicator.label}`, 10, true, severityColor);
                    addText(`   ${indicator.description}`, 9);
                });

                // Recommended Actions
                addSection("RECOMMENDED ACTIONS");
                recommendedActions.forEach((action) => {
                    addText(action.title.toUpperCase(), 11, true);
                    action.actions.forEach((item) => {
                        addText(`• ${item}`, 10);
                    });
                    yPos += 2;
                });

                // Investigation Timeline
                if (yPos > 200) {
                    doc.addPage();
                    yPos = 20;
                }
                addSection("INVESTIGATION TIMELINE");
                investigationTimeline.forEach((event) => {
                    addText(`[${event.time}] ${event.title}`, 10, true);
                    addText(event.description, 9);
                });

                // AI Confidence Metrics
                addSection("AI CONFIDENCE METRICS");
                autoTable(doc, {
                    startY: yPos,
                    head: [['Metric', 'Value']],
                    body: [
                        ['Fraud Probability', '84%'],
                        ['Model Confidence', '95%'],
                        ['False Positive Probability', '8%'],
                        ['Explainability Score', 'High'],
                    ],
                    theme: 'striped',
                    headStyles: { fillColor: [37, 99, 235] },
                    margin: { left: margin, right: margin },
                });
                yPos = (doc as any).lastAutoTable.finalY + 10;

                // Risk Contribution
                addSection("RISK CONTRIBUTION BREAKDOWN");
                autoTable(doc, {
                    startY: yPos,
                    head: [['Risk Factor', 'Contribution']],
                    body: riskContribution.map(item => [item.factor, `${item.percentage}%`]),
                    theme: 'striped',
                    headStyles: { fillColor: [37, 99, 235] },
                    margin: { left: margin, right: margin },
                });
                yPos = (doc as any).lastAutoTable.finalY + 10;

                // Footer
                const pageCount = doc.getNumberOfPages();
                for (let i = 1; i <= pageCount; i++) {
                    doc.setPage(i);
                    doc.setFontSize(8);
                    doc.setTextColor(128, 128, 128);
                    doc.text(
                        `Page ${i} of ${pageCount} | Report ID: ${transaction?.transaction_id || anomaly?.transactionId || "report"}-${Date.now()} | Blockchain Anomaly AI`,
                        pageWidth / 2,
                        doc.internal.pageSize.getHeight() - 10,
                        { align: "center" }
                    );
                }

                // Download PDF
                doc.save(`Anomaly_Report_${transaction?.transaction_id || anomaly?.transactionId || "report"}_${new Date().toISOString().split('T')[0]}.pdf`);

                message.success({
                    content: 'PDF report downloaded successfully!',
                    key: 'pdf-download',
                    duration: 2
                });
            } catch (error) {
                console.error('Error generating PDF:', error);
                message.error({ content: 'Failed to generate PDF report', key: 'pdf-download', duration: 2 });
            }
        }, 500);
    };

    const downloadReportMenu = {
        items: [
            {
                key: "preview",
                label: "Preview Report",
                icon: <EyeOutlined />,
                onClick: handlePreviewReport,
            },
            {
                key: "download",
                label: "Download as PDF",
                icon: <FilePdfOutlined />,
                onClick: handleDownloadPDF,
            },
        ]
    };

    // Menu items for actions
    const downloadReportMenu = {
        items: [
            {
                key: "preview",
                label: "Preview Report",
                icon: <EyeOutlined />,
                onClick: handlePreviewReport,
            },
            {
                key: "download",
                label: "Download as PDF",
                icon: <FilePdfOutlined />,
                onClick: handleDownloadPDF,
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

    // Loading state
    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading anomaly details...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error || !anomaly) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-lg">
                    <div className="flex items-center gap-2 mb-4">
                        <svg className="h-5 w-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="text-sm font-semibold text-red-800">Error Loading Anomaly</span>
                    </div>
                    <p className="text-sm text-red-700 mb-4">{error || "Anomaly not found"}</p>
                    <div className="text-xs text-gray-600 mb-4">
                        <p>Transaction ID: <code className="bg-gray-100 px-1 py-0.5 rounded">{transactionId}</code></p>
                        <p className="mt-1">Check browser console for more details</p>
                    </div>
                    <button
                        onClick={() => navigate("/anomalies")}
                        className="px-4 py-2 text-white rounded-lg text-sm"
                    >
                        Back to Anomalies
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div style={{ padding: 24, backgroundColor: "#f5f5f5", minHeight: "100vh" }}>
            {/* Header */}
            <div style={{ marginBottom: 24 }}>
                <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
                    <Col>
                        <button
                            onClick={() => navigate(-1)}
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
                                    Transaction ID: <code className="text-blue-600">{anomaly?.transactionId}</code>
                                </p>
                                {/* <span style={{ color: "#666" }}>Dashboard</span>
                <span style={{ color: "#666" }}>›</span>
                <span style={{ color: "#666" }}>Investigations</span>
                <span style={{ color: "#666" }}>›</span>
                <span style={{ color: "#1890ff" }}>{transactionData.id}</span> */}
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
                            <Dropdown menu={moreActionsMenu} placement="bottomRight">
                                <Button icon={<MoreOutlined />} size="large" />
                            </Dropdown>
                        </Space>
                    </Col>
                </Row>
            </div>

            {/* Transaction Header Card */}
            <Card style={{ marginBottom: 24 }}>
                <Row gutter={[24, 24]}>
                    <Col span={18}>
                        <Row gutter={[32, 16]}>
                            <Col span={8}>
                                <Space direction="vertical" size={0}>
                                    <span style={{ color: "#666", fontSize: 12 }}>Transaction ID</span>
                                    <span style={{ fontSize: 18, fontWeight: 600 }}>{transaction?.transaction_id || anomaly?.transactionId || "N/A"}</span>
                                </Space>
                            </Col>
                            <Col span={8}>
                                <Space direction="vertical" size={0}>
                                    <span style={{ color: "#666", fontSize: 12 }}>Date & Time</span>
                                    <span style={{ fontSize: 16 }}>{transaction?.transaction_timestamp ? format(new Date(transaction.transaction_timestamp), "dd MMM yyyy, hh:mm a") : "N/A"}</span>
                                </Space>
                            </Col>
                            <Col span={8}>
                                <Space direction="vertical" size={0}>
                                    <span style={{ color: "#666", fontSize: 12 }}>Amount</span>
                                    <span style={{ fontSize: 18, fontWeight: 600, color: "#ff4d4f" }}>
                                        {transaction ? `${transaction.currency || "INR"} ${transaction.amount?.toLocaleString() || "0"}` : "N/A"}
                                    </span>
                                </Space>
                            </Col>
                            <Col span={8}>
                                <Space direction="vertical" size={0}>
                                    <span style={{ color: "#666", fontSize: 12 }}>Client Name</span>
                                    <span style={{ fontSize: 16 }}>{transaction?.client_name}</span>
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
                                    <span style={{ fontSize: 16 }}>{transaction?.client_id || anomaly?.clientId || "N/A"}</span>
                                </Space>
                            </Col>
                            <Col span={8}>
                                <Space direction="vertical" size={0}>
                                    <span style={{ color: "#666", fontSize: 12 }}>Channel</span>
                                    <span style={{ fontSize: 16 }}>{transaction?.transaction_category || transaction?.blockchain_network || "N/A"}</span>
                                </Space>
                            </Col>
                            <Col span={8}>
                                <Space direction="vertical" size={0}>
                                    <span style={{ color: "#666", fontSize: 12 }}>Status</span>
                                    <Tag color="orange">{anomaly?.reviewStatus || transaction?.transaction_status || "N/A"}</Tag>
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
                                    <span style={{ fontSize: 16 }}>{anomaly?.modelName || "N/A"} {anomaly?.modelVersion ? `v${anomaly?.modelVersion}` : ""}</span>
                                </Space>
                            </Col>
                            <Col span={8}>
                                <Space direction="vertical" size={0}>
                                    <span style={{ color: "#666", fontSize: 12 }}>Detected At</span>
                                    <span style={{ fontSize: 16 }}>{anomaly?.detectedAt ? format(new Date(anomaly.detectedAt), "MMM dd, yyyy HH:mm:ss") : "N/A"}</span>
                                </Space>
                            </Col>
                        </Row>
                    </Col>
                    <Col span={6}>
                        <div style={{ textAlign: "center" }}>
                            <div style={{ marginBottom: 8, color: "#666", fontSize: 14 }}>Risk Score</div>
                            <Progress
                                type="circle"
                                percent={anomaly?.anomalyScore ? Math.round(anomaly.anomalyScore * 100) : 0}
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
                            <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>{anomaly?.severity || "Unknown"} Risk</div>
                            <div style={{ fontSize: 12, fontWeight: 600 }}>{anomaly?.anomalyCategory || "Unknown"}</div>
                        </div>
                    </Col>
                </Row>
            </Card>

            {/* Main Content */}
            <Row gutter={24}>
                <Col span={16}>
                    {/* AI Generated Narrative */}
                    <Card
                        title={
                            <Space>
                                <ExperimentOutlined />
                                AI Generated Narrative
                            </Space>
                        }
                        extra={
                            <Space>
                                <Select
                                    value={selectedLanguage}
                                    onChange={setSelectedLanguage}
                                    style={{ width: 150 }}
                                    options={languages.map(lang => ({
                                        value: lang.value,
                                        label: (
                                            <Space>
                                                <span>{lang.flag}</span>
                                                <span>{lang.label}</span>
                                            </Space>
                                        ),
                                    }))}
                                    suffixIcon={<GlobalOutlined />}
                                />
                                <Button
                                    type={isPlaying ? "primary" : "default"}
                                    icon={isPlaying ? <PauseCircleOutlined /> : <SoundOutlined />}
                                    onClick={handlePlayNarrative}
                                >
                                    {isPlaying ? "Stop Audio" : "Play Audio"}
                                </Button>
                            </Space>
                        }
                        style={{ marginBottom: 24 }}
                    >
                        <Tabs
                            activeKey={selectedPersona}
                            onChange={setSelectedPersona}
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
                                        <div style={{ fontSize: 14, lineHeight: 1.8, color: "#595959", whiteSpace: "pre-line", padding: "16px 0" }}>
                                            {aiNarratives["fraud-analyst"].content}
                                        </div>
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
                                            {aiNarratives["compliance-officer"].content}
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
                                            {aiNarratives["relationship-manager"].content}
                                        </div>
                                    ),
                                },
                                {
                                    key: "operations-team",
                                    label: (
                                        <Space>
                                            <TeamOutlined />
                                            Operations Team
                                        </Space>
                                    ),
                                    children: (
                                        <div style={{ fontSize: 14, lineHeight: 1.8, color: "#595959", whiteSpace: "pre-line", padding: "16px 0" }}>
                                            {aiNarratives["operations-team"].content}
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
                                            {aiNarratives["executive-summary"].content}
                                        </div>

                                    ),
                                },
                            ]}
                        />
                    </Card>

  {/* Anomaly Reasons */}

    {anomaly.anomalyReasons && anomaly.anomalyReasons.length > 0 ? (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Anomaly Reasons</h2>
                <div className="space-y-3">
                  {anomaly.anomalyReasons.map((reason, index) => (
                    <div
                      key={index}
                      className="p-4 bg-red-50 border border-red-200 rounded-lg"
                    >
                      <div className="flex items-start gap-2">
                        <svg className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <div className="flex-1">
                          <div className="text-sm font-medium text-red-900">{reason.reasonCode}</div>
                          <div className="text-sm text-red-700 mt-1">{reason.description}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Anomaly Reasons</h2>
                <p className="text-sm text-gray-600">No specific reasons available for this anomaly.</p>
              </div>
            )}
  
                    {/* Key Risk Indicators */}
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
                            {riskIndicators.map((indicator) => (
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

                    {/* Recommended Actions */}
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
                            {recommendedActions.map((action) => (
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
                </Col>

                <Col span={8}>
                    {/* Transaction Snapshot */}
                    <Card
                        title={
                            <Space>
                                <LineChartOutlined />
                                Transaction Snapshot
                            </Space>
                        }
                        style={{ marginBottom: 24 }}
                    >
                        <Descriptions column={1} size="small">
                            <Descriptions.Item label="Transaction Type">
                                {transaction?.transaction_type || "N/A"}
                            </Descriptions.Item>
                            <Descriptions.Item label="Amount">
                                <span style={{ fontWeight: 600 }}>{transaction ? `${transaction.currency || "INR"} ${transaction.amount?.toLocaleString() || "0"}` : "N/A"}</span>
                            </Descriptions.Item>
                            <Descriptions.Item label="Blockchain Network">
                                {transaction?.blockchain_network || "N/A"}
                            </Descriptions.Item>
                            <Descriptions.Item label="Transaction Status">
                                <Tag color="blue">{transaction?.transaction_status || "N/A"}</Tag>
                            </Descriptions.Item>
                            <Descriptions.Item label="From Wallet">
                                {transaction?.from_wallet_address ? `${transaction.from_wallet_address.substring(0, 10)}...` : "N/A"}
                            </Descriptions.Item>
                            <Descriptions.Item label="To Wallet">
                                {transaction?.to_wallet_address ? `${transaction.to_wallet_address.substring(0, 10)}...` : "N/A"}
                            </Descriptions.Item>
                            <Descriptions.Item label="Block Number">{transaction?.block_number || "N/A"}</Descriptions.Item>
                            <Descriptions.Item label="Chain ID">{transaction?.chain_id || "N/A"}</Descriptions.Item>
                        </Descriptions>
                    </Card>

                    {/* AI Confidence */}
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

                    {/* Risk Contribution */}
                    <Card
                        title="Risk Contribution"
                        style={{ marginBottom: 24 }}
                    >
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
                            {riskContribution.map((item, idx) => (
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

                    {/* Investigation Timeline */}
                    <Card
                        title={
                            <Space>
                                <ClockCircleOutlined />
                                Investigation Timeline
                            </Space>
                        }
                        style={{ marginBottom: 24 }}
                    >
                        <Timeline
                            items={investigationTimeline.map((event) => ({
                                color: event.type === "error" ? "red" : event.type === "warning" ? "orange" : "blue",
                                children: (
                                    <div>
                                        <div style={{ fontWeight: 600, marginBottom: 4 }}>
                                            {event.time} - {event.title}
                                        </div>
                                        <div style={{ fontSize: 12, color: "#666" }}>{event.description}</div>
                                    </div>
                                ),
                            }))}
                        />
                    </Card>

                    {/* Related Entities */}
                    {/* <Card title="Related Entities">
                        <Space direction="vertical" size={12} style={{ width: "100%" }}>
                            {relatedEntities.map((entity, idx) => (
                                <div
                                    key={idx}
                                    style={{
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                        padding: "8px 0",
                                        borderBottom: idx < relatedEntities.length - 1 ? "1px solid #f0f0f0" : "none",
                                    }}
                                >
                                    <Space>
                                        {entity.icon}
                                        <span>{entity.label}</span>
                                    </Space>
                                    <Badge count={entity.count} style={{ backgroundColor: "#1890ff" }} />
                                </div>
                            ))}
                        </Space>
                        <Divider />
                        <Button type="link" block style={{ padding: 0 }}>
                            View Entity Graph →
                        </Button>
                    </Card> */}
                </Col>
            </Row>

            {/* Report Preview Modal */}
            <Modal
                title={
                    <Space>
                        <FilePdfOutlined style={{ color: "#1890ff" }} />
                        <span>Anomaly Investigation Report - {transaction?.transaction_id || anomaly?.transactionId || "N/A"}</span>
                    </Space>
                }
                open={isReportModalVisible}
                onCancel={() => setIsReportModalVisible(false)}
                width={900}
                footer={[
                    <Button key="close" onClick={() => setIsReportModalVisible(false)}>
                        Close
                    </Button>,
                    <Button
                        key="download"
                        type="primary"
                        icon={<DownloadOutlined />}
                        onClick={() => {
                            setIsReportModalVisible(false);
                            handleDownloadPDF();
                        }}
                    >
                        Download PDF
                    </Button>,
                ]}
                style={{ top: 20 }}
            >
                <div
                    ref={reportRef}
                    style={{
                        maxHeight: "70vh",
                        overflowY: "auto",
                        padding: "24px",
                        backgroundColor: "#fff",
                        fontFamily: "monospace",
                        fontSize: "12px",
                        lineHeight: "1.6",
                        whiteSpace: "pre-wrap",
                        border: "1px solid #f0f0f0",
                        borderRadius: "4px",
                    }}
                >
                    <div style={{ textAlign: "center", marginBottom: 24 }}>
                        <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>
                            BLOCKCHAIN ANOMALY INTELLIGENCE REPORT
                        </h2>
                        <Divider style={{ margin: "16px 0" }} />
                    </div>

                    <Descriptions bordered column={2} size="small" style={{ marginBottom: 24 }}>
                        <Descriptions.Item label="Transaction ID" span={2}>
                            <strong>{transaction?.transaction_id || anomaly?.transactionId || "N/A"}</strong>
                        </Descriptions.Item>
                        <Descriptions.Item label="Report Generated">
                            {new Date().toLocaleString()}
                        </Descriptions.Item>
                        <Descriptions.Item label="Risk Score">
                            <Tag color="red" style={{ fontSize: 14, padding: "4px 12px" }}>
                                {anomaly?.anomalyScore ? Math.round(anomaly.anomalyScore * 100) : 0}/100 - {anomaly?.severity || "Unknown"} Risk
                            </Tag>
                        </Descriptions.Item>
                    </Descriptions>

                    <Card title="Transaction Details" size="small" style={{ marginBottom: 16 }}>
                        <Descriptions column={2} size="small">
                            <Descriptions.Item label="Date & Time" span={2}>
                                {transaction?.transaction_timestamp ? format(new Date(transaction.transaction_timestamp), "dd MMM yyyy, hh:mm a") : "N/A"}
                            </Descriptions.Item>
                            <Descriptions.Item label="Amount" span={2}>
                                <strong style={{ fontSize: 16, color: "#ff4d4f" }}>
                                    {transaction ? `${transaction.currency || "INR"} ${transaction.amount?.toLocaleString() || "0"}` : "N/A"}
                                </strong>
                            </Descriptions.Item>
                            <Descriptions.Item label="Channel">{transaction?.blockchain_network || "N/A"}</Descriptions.Item>
                            <Descriptions.Item label="Status">
                                <Tag color="orange">{anomaly?.reviewStatus || transaction?.transaction_status || "N/A"}</Tag>
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
                            <Descriptions.Item label="Destination Account">
                                {transaction?.to_account || "N/A"}
                            </Descriptions.Item>
                            <Descriptions.Item label="Transaction Type" span={2}>
                                {transaction?.transaction_type || "N/A"}
                            </Descriptions.Item>
                        </Descriptions>
                    </Card>

                    <Card title="AI-Generated Narrative (Fraud Analyst)" size="small" style={{ marginBottom: 16 }}>
                        <div style={{ fontSize: 13, lineHeight: 1.6, color: "#595959" }}>
                            {aiNarratives["fraud-analyst"].content}
                        </div>
                    </Card>

                    <Card title="Key Risk Indicators" size="small" style={{ marginBottom: 16 }}>
                        <Space direction="vertical" size={8} style={{ width: "100%" }}>
                            {riskIndicators.map((indicator, idx) => (
                                <Alert
                                    key={idx}
                                    message={
                                        <strong>
                                            [{indicator.severity.toUpperCase()}] {indicator.label}
                                        </strong>
                                    }
                                    description={indicator.description}
                                    type={indicator.severity === "high" ? "error" : "warning"}
                                    showIcon
                                    style={{ fontSize: 12 }}
                                />
                            ))}
                        </Space>
                    </Card>

                    <Card title="Recommended Actions" size="small" style={{ marginBottom: 16 }}>
                        <Row gutter={16}>
                            {recommendedActions.map((action) => (
                                <Col span={8} key={action.priority}>
                                    <div style={{ marginBottom: 12 }}>
                                        <Tag color={getPriorityColor(action.priority)} style={{ marginBottom: 8 }}>
                                            {action.title}
                                        </Tag>
                                        <ul style={{ margin: 0, paddingLeft: 20, fontSize: 12 }}>
                                            {action.actions.map((item, idx) => (
                                                <li key={idx} style={{ marginBottom: 4 }}>
                                                    {item}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </Col>
                            ))}
                        </Row>
                    </Card>

                    <Card title="Investigation Timeline" size="small" style={{ marginBottom: 16 }}>
                        <Timeline
                            items={investigationTimeline.map((event) => ({
                                color: event.type === "error" ? "red" : event.type === "warning" ? "orange" : "blue",
                                children: (
                                    <div style={{ fontSize: 12 }}>
                                        <strong>
                                            {event.time} - {event.title}
                                        </strong>
                                        <div style={{ color: "#666", marginTop: 4 }}>{event.description}</div>
                                    </div>
                                ),
                            }))}
                        />
                    </Card>

                    <Card title="AI Confidence Metrics" size="small" style={{ marginBottom: 16 }}>
                        <Descriptions column={2} size="small">
                            <Descriptions.Item label="Fraud Probability">84%</Descriptions.Item>
                            <Descriptions.Item label="Model Confidence">95%</Descriptions.Item>
                            <Descriptions.Item label="False Positive Probability">8%</Descriptions.Item>
                            <Descriptions.Item label="Explainability Score">
                                <Tag color="green">High</Tag>
                            </Descriptions.Item>
                        </Descriptions>
                    </Card>

                    <Card title="Risk Contribution Breakdown" size="small" style={{ marginBottom: 16 }}>
                        <Space direction="vertical" size={4} style={{ width: "100%" }}>
                            {riskContribution.map((item, idx) => (
                                <div key={idx} style={{ fontSize: 12 }}>
                                    <strong>{item.factor}:</strong> {item.percentage}%
                                </div>
                            ))}
                        </Space>
                    </Card>

                    <Divider />

                    <div style={{ fontSize: 11, color: "#999", textAlign: "center", marginTop: 24 }}>
                        <p>
                            <strong>COMPLIANCE NOTICE</strong>
                        </p>
                        <p>
                            This report is generated by Blockchain Anomaly AI for compliance and risk assessment
                            purposes.
                            <br />
                            All findings should be reviewed by qualified personnel before taking action.
                            <br />
                            This is a confidential document.
                        </p>
                        <p>
                            Report ID: {transaction?.transaction_id || anomaly?.transactionId || "report"}-{Date.now()} | Generated by: Blockchain Anomaly AI
                            System
                        </p>
                    </div>
                </div>
            </Modal>
        </div>
    );
};

export default AnomalyNarrativePage;
