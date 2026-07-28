import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Row, Col, Modal, message, Spin, Alert, Button } from "antd";
import { ReloadOutlined } from "@ant-design/icons";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

// Hooks
import { useAnomalyData, useNarrativeAudio, useShapNarrative } from "./hooks";

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
    ReportPreview,
} from "./components";

// Constants
import {
    RISK_INDICATORS,
    RISK_CONTRIBUTION,
    INVESTIGATION_TIMELINE,
    RECOMMENDED_ACTIONS,
    NARRATIVE_TRANSLATIONS,
} from "./constants";
import { format } from "date-fns";

const AnomalyNarrativePage: React.FC = () => {
    const navigate = useNavigate();

    // Data fetching
    const { anomaly, transaction, loading, error, transactionId } = useAnomalyData();
    
    // UI state
    const [selectedPersona, setSelectedPersona] = useState<string>("fraud-analyst");
    
    // SHAP-based narrative generation with persona support
    const { 
        narrative: shapNarrative, 
        loading: narrativeLoading, 
        error: narrativeError,
        refetch: refetchNarrative 
    } = useShapNarrative(anomaly?.anomalyId, true, selectedPersona);

    // UI state for modal
    const [isReportModalVisible, setIsReportModalVisible] = useState(false);

    // Narrative translations (English only) - will be replaced by SHAP narrative
    const aiNarratives = NARRATIVE_TRANSLATIONS.en;

    // Audio playback
    const { isPlaying, handlePlayNarrative } = useNarrativeAudio(
        aiNarratives,
        selectedPersona
    );
    
    // Handle persona change
    const handlePersonaChange = (newPersona: string) => {
        setSelectedPersona(newPersona);
        // Regenerate narrative with new persona
        if (anomaly?.anomalyId) {
            refetchNarrative(newPersona);
        }
    };

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

    // Generate risk contribution from anomaly reasons
    const generateRiskContribution = () => {
        if (!anomaly?.anomalyReasons || anomaly.anomalyReasons.length === 0) {
            // Fallback to static data if no anomaly reasons
            return RISK_CONTRIBUTION;
        }

        const reasons = anomaly.anomalyReasons;
        
        // Color palette for risk factors (from high to low risk)
        const colors = ["#ff4d4f", "#ff7a45", "#ffa940", "#ffc53d", "#ffec3d", "#fadb14"];
        
        // Distribute percentages: first reason gets higher weight
        // Using a weighted distribution: first gets 40%, then decreasing
        const weights = reasons.map((_, index) => {
            return Math.max(10, 50 - (index * 10));
        });
        
        const totalWeight = weights.reduce((sum, w) => sum + w, 0);
        
        return reasons.map((reason, index) => ({
            factor: reason.description || reason.reasonCode || `Risk Factor ${index + 1}`,
            percentage: Math.round((weights[index] / totalWeight) * 100),
            color: colors[index % colors.length]
        }));
    };

    const riskContribution = generateRiskContribution();

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
                addText(`Transaction ID: ${transactionData.id}`, 11, true);
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
                RISK_INDICATORS.forEach((indicator, idx) => {
                    const severityColor = indicator.severity === 'high' ? [220, 38, 38] : [245, 158, 11];
                    addText(`${idx + 1}. [${indicator.severity.toUpperCase()}] ${indicator.label}`, 10, true, severityColor);
                    addText(`   ${indicator.description}`, 9);
                });

                // Recommended Actions
                addSection("RECOMMENDED ACTIONS");
                RECOMMENDED_ACTIONS.forEach((action) => {
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
                INVESTIGATION_TIMELINE.forEach((event) => {
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
                        `Page ${i} of ${pageCount} | Report ID: ${transactionData.id}-${Date.now()} | Blockchain Anomaly AI`,
                        pageWidth / 2,
                        doc.internal.pageSize.getHeight() - 10,
                        { align: "center" }
                    );
                }

                // Download PDF
                doc.save(`Anomaly_Report_${transactionData.id}_${new Date().toISOString().split('T')[0]}.pdf`);

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

    // Main component with refactored structure
    return (
        <div style={{ padding: 24, backgroundColor: "#f5f5f5", minHeight: "100vh" }}>
            {/* Header with navigation and actions */}
            <AnomalyHeader
                transactionId={transactionData.id}
                onBack={() => navigate(-1)}
                onDownloadPDF={handleDownloadPDF}
                onPreviewReport={handlePreviewReport}
            />

            {/* Transaction overview card with risk score */}
            <TransactionHeaderCard
                anomaly={anomaly}
                transaction={transaction}
            />

            {/* Main content grid */}
            <Row gutter={24}>
                {/* Left column - Main content */}
                <Col span={16}>
                    {/* SHAP-Generated AI Narrative */}
                    {narrativeLoading && (
                        <Alert
                            message="Generating AI Narrative"
                            description={
                                <div className="flex items-center gap-2">
                                    <Spin size="small" />
                                    <span>Using SHAP explainability and Cortex AI to generate insights...</span>
                                </div>
                            }
                            type="info"
                            showIcon
                            style={{ marginBottom: 24 }}
                        />
                    )}
                    
                    {narrativeError && (
                        <Alert
                            message="Narrative Generation Failed"
                            description={
                                <div>
                                    <p>{narrativeError}</p>
                                    <Button 
                                        icon={<ReloadOutlined />} 
                                        onClick={() => refetchNarrative()}
                                        size="small"
                                        style={{ marginTop: 8 }}
                                    >
                                        Retry
                                    </Button>
                                </div>
                            }
                            type="warning"
                            showIcon
                            style={{ marginBottom: 24 }}
                        />
                    )}
                    
                    {shapNarrative && (
                        <AIGeneratedNarrative
                            isPlaying={isPlaying}
                            onPlayPause={handlePlayNarrative}
                            selectedPersona={selectedPersona}
                            onPersonaChange={handlePersonaChange}
                            narratives={{
                                "fraud-analyst": {
                                    title: "AI-Generated Explanation (SHAP + Cortex)",
                                    content: shapNarrative.narrative
                                },
                                "compliance-officer": {
                                    title: "AI-Generated Explanation (SHAP + Cortex)",
                                    content: shapNarrative.narrative
                                },
                                "relationship-manager": {
                                    title: "AI-Generated Explanation (SHAP + Cortex)",
                                    content: shapNarrative.narrative
                                },
                                "auditor": {
                                    title: "AI-Generated Explanation (SHAP + Cortex)",
                                    content: shapNarrative.narrative
                                },
                                "regulator": {
                                    title: "AI-Generated Explanation (SHAP + Cortex)",
                                    content: shapNarrative.narrative
                                },
                                "operations-team": {
                                    title: "AI-Generated Explanation (SHAP + Cortex)",
                                    content: shapNarrative.narrative
                                },
                                "executive-summary": {
                                    title: "AI-Generated Explanation (SHAP + Cortex)",
                                    content: shapNarrative.narrative
                                }
                            }}
                            shapContributors={shapNarrative.shap_contributors}
                            predictionLabel={shapNarrative.prediction_label}
                            modelUsed={shapNarrative.model_used}
                        />
                    )}


                    {/* Anomaly reasons from API */}
                    <AnomalyReasonsCard anomaly={anomaly} />

                    {/* Key risk indicators */}
                    <KeyRiskIndicators indicators={RISK_INDICATORS} />

                    {/* Recommended actions by priority */}
                    <RecommendedActions actions={RECOMMENDED_ACTIONS} />
                </Col>

                {/* Right column - Sidebar widgets */}
                <Col span={8}>
                    {/* Transaction details snapshot */}
                    <TransactionSnapshot transaction={transaction} anomaly={anomaly} />

                    {/* AI confidence metrics */}
                    <AIConfidence />

                    {/* Risk contribution breakdown */}
                    <RiskContribution factors={riskContribution} />

                    {/* Investigation timeline */}
                    <InvestigationTimeline events={INVESTIGATION_TIMELINE} />
                </Col>
            </Row>

            {/* PDF Preview Modal */}
            <Modal
                title="Report Preview"
                open={isReportModalVisible}
                onCancel={() => setIsReportModalVisible(false)}
                footer={null}
                width={1000}
            >
                <ReportPreview
                    anomaly={anomaly}
                    transaction={transaction}
                    narratives={aiNarratives}
                    riskIndicators={RISK_INDICATORS}
                    recommendedActions={RECOMMENDED_ACTIONS}
                    timeline={INVESTIGATION_TIMELINE}
                    riskContribution={riskContribution}
                />
            </Modal>
        </div>
    );
};

export default AnomalyNarrativePage;
