import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import anomalyService from "../../services/anomaly/anomalyService";
import transactionService, { Transaction } from "../../services/transaction/transactionService";
import { AnomalyResult } from "../../types/anomaly.types";
import { RiskBadge, StatusBadge } from "../../components/Common/Badges";
import { format } from "date-fns";

const NarrativePage: React.FC = () => {
  const { anomalyId } = useParams<{ anomalyId: string }>(); // Actually receives transactionId from route
  const navigate = useNavigate();
  
  const [anomaly, setAnomaly] = useState<AnomalyResult | null>(null);
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Static narrative for now
  const staticNarrative = {
    title: "High-Risk Transaction Anomaly Detected",
    summary: "This transaction exhibits multiple risk indicators including unusual amount patterns, timing anomalies, and behavioral deviations from the client's historical profile.",
    detailed_explanation: `Our AI-powered anomaly detection system has identified several concerning patterns in this transaction:

1. Transaction Amount Analysis: The transaction amount significantly deviates from the client's typical transaction patterns, falling outside the expected range based on historical data.

2. Temporal Pattern Detection: The transaction timing shows unusual characteristics, occurring during non-business hours or at an atypical frequency for this client.

3. Network Behavior Analysis: The blockchain network patterns associated with this transaction differ from the client's established transaction graph.

4. Risk Score Aggregation: Multiple detection models have flagged this transaction, with consensus across different analytical approaches indicating elevated risk.`,
    risk_factors: [
      "Transaction amount exceeds 3 standard deviations from client's historical average",
      "Unusual transaction timing pattern detected",
      "Wallet address shows connections to previously flagged entities",
      "Transaction velocity exceeds normal parameters for this client",
      "Blockchain metadata contains irregular patterns"
    ],
    recommendations: [
      "Immediate manual review by compliance team recommended",
      "Contact client to verify transaction authenticity",
      "Review client's recent transaction history for additional anomalies",
      "Consider temporary hold on similar transactions pending verification",
      "Update client risk profile based on investigation findings"
    ],
    model_used: "Ensemble ML Model (Isolation Forest + LSTM + XGBoost)",
    confidence_score: 0.87
  };

  useEffect(() => {
    if (!anomalyId) return;
    
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log("Fetching anomaly for transaction ID:", anomalyId);
        
        // Fetch anomaly by transaction ID (the route param is actually transactionId)
        const anomalyData = await anomalyService.getByTransactionId(anomalyId);
        console.log("Anomaly data fetched:", anomalyData);
        setAnomaly(anomalyData);
        
        // Fetch transaction details
        try {
          console.log("Fetching transaction details for:", anomalyId);
          const txData = await transactionService.getById(anomalyId);
          console.log("Transaction data fetched:", txData);
          setTransaction(txData);
        } catch (txErr) {
          console.warn("Failed to fetch transaction:", txErr);
        }
      } catch (err) {
        console.error("Failed to fetch anomaly:", err);
        setError(err instanceof Error ? err.message : "Failed to load anomaly details");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [anomalyId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-sm text-gray-600">Loading anomaly details...</p>
        </div>
      </div>
    );
  }

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
            <p>Transaction ID: <code className="bg-gray-100 px-1 py-0.5 rounded">{anomalyId}</code></p>
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <button
                onClick={() => navigate(-1)}
                className="text-sm text-gray-600 hover:text-gray-900 mb-2 flex items-center gap-1"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Anomaly Details</h1>
              <p className="text-sm text-gray-600 mt-1">
                Transaction ID: <code className="text-blue-600">{anomaly.transactionId}</code>
              </p>
            </div>
            <div className="flex items-center gap-3">
              <RiskBadge severity={anomaly.severity} />
              <StatusBadge status={anomaly.reviewStatus} />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Anomaly Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Anomaly Summary Card */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Anomaly Summary</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-600">Anomaly ID</div>
                  <div className="text-sm font-medium text-gray-900">{anomaly.anomalyId}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Category</div>
                  <div className="text-sm font-medium text-gray-900">{anomaly.anomalyCategory}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Risk Score</div>
                  <div className="text-sm font-medium text-gray-900">
                    {(anomaly.anomalyScore * 100).toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Confidence</div>
                  <div className="text-sm font-medium text-gray-900">
                    {(anomaly.confidence * 100).toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Model</div>
                  <div className="text-sm font-medium text-gray-900">
                    {anomaly.modelName || "N/A"} {anomaly.modelVersion ? `v${anomaly.modelVersion}` : ""}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Detected At</div>
                  <div className="text-sm font-medium text-gray-900">
                    {format(new Date(anomaly.detectedAt), "MMM dd, yyyy HH:mm:ss")}
                  </div>
                </div>
              </div>
            </div>

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

            {/* Anomaly Types */}
            {anomaly.anomalyTypes && anomaly.anomalyTypes.length > 0 ? (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Detected Anomaly Types</h2>
                <div className="flex flex-wrap gap-2">
                  {anomaly.anomalyTypes.map((type, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                    >
                      {type}
                    </span>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Detected Anomaly Types</h2>
                <p className="text-sm text-gray-600">No specific types classified for this anomaly.</p>
              </div>
            )}

            {/* Transaction Details */}
            {transaction && (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Transaction Details</h2>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600">Transaction Hash</div>
                      <div className="text-sm font-mono text-gray-900 break-all">{transaction.transaction_hash}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Type</div>
                      <div className="text-sm font-medium text-gray-900">{transaction.transaction_type}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Amount</div>
                      <div className="text-sm font-medium text-gray-900">
                        {transaction.currency} {(transaction.amount || 0).toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Status</div>
                      <div className="text-sm font-medium text-gray-900">{transaction.transaction_status}</div>
                    </div>
                    {transaction.from_account && (
                      <div>
                        <div className="text-sm text-gray-600">From Account</div>
                        <div className="text-sm font-medium text-gray-900">{transaction.from_account}</div>
                      </div>
                    )}
                    {transaction.to_account && (
                      <div>
                        <div className="text-sm text-gray-600">To Account</div>
                        <div className="text-sm font-medium text-gray-900">{transaction.to_account}</div>
                      </div>
                    )}
                    {transaction.from_wallet_address && (
                      <div>
                        <div className="text-sm text-gray-600">From Wallet</div>
                        <div className="text-sm font-mono text-xs text-gray-900 break-all">{transaction.from_wallet_address}</div>
                      </div>
                    )}
                    {transaction.to_wallet_address && (
                      <div>
                        <div className="text-sm text-gray-600">To Wallet</div>
                        <div className="text-sm font-mono text-xs text-gray-900 break-all">{transaction.to_wallet_address}</div>
                      </div>
                    )}
                    {transaction.blockchain_network && (
                      <div>
                        <div className="text-sm text-gray-600">Blockchain Network</div>
                        <div className="text-sm font-medium text-gray-900">{transaction.blockchain_network}</div>
                      </div>
                    )}
                    {transaction.chain_id && (
                      <div>
                        <div className="text-sm text-gray-600">Chain ID</div>
                        <div className="text-sm font-medium text-gray-900">{transaction.chain_id}</div>
                      </div>
                    )}
                    {transaction.block_number && (
                      <div>
                        <div className="text-sm text-gray-600">Block Number</div>
                        <div className="text-sm font-medium text-gray-900">{transaction.block_number}</div>
                      </div>
                    )}
                    <div>
                      <div className="text-sm text-gray-600">Timestamp</div>
                      <div className="text-sm font-medium text-gray-900">
                        {format(new Date(transaction.transaction_timestamp), "MMM dd, yyyy HH:mm:ss")}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* AI Narrative Section */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">AI Narrative Explanation</h2>
                <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                  AI Generated
                </span>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="text-md font-semibold text-gray-900 mb-2">{staticNarrative.title}</h3>
                  <p className="text-sm text-gray-700">{staticNarrative.summary}</p>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-blue-900 mb-2">Detailed Explanation</h4>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{staticNarrative.detailed_explanation}</p>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-orange-900 mb-2">Risk Factors</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {staticNarrative.risk_factors.map((f, i) => (
                      <li key={i} className="text-sm text-gray-700">{f}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="text-sm font-semibold text-green-900 mb-2">Recommendations</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {staticNarrative.recommendations.map((r, i) => (
                      <li key={i} className="text-sm text-gray-700">{r}</li>
                    ))}
                  </ul>
                </div>

                <p className="text-xs text-gray-500 pt-2 border-t border-gray-200">
                  Generated by {staticNarrative.model_used} • Confidence: {(staticNarrative.confidence_score * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Client Information */}
            {(anomaly.clientId || transaction?.client_id) && (
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Client Information</h3>
                <div className="space-y-2">
                  <div>
                    <div className="text-xs text-gray-600">Client ID</div>
                    <div className="text-sm font-medium text-gray-900">{anomaly.clientId || transaction?.client_id}</div>
                  </div>
                  {transaction?.client_name && (
                    <div>
                      <div className="text-xs text-gray-600">Client Name</div>
                      <div className="text-sm font-medium text-gray-900">{transaction.client_name}</div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Case Management */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Case Management</h3>
              <div className="space-y-2">
                {anomaly.caseId && (
                  <div>
                    <div className="text-xs text-gray-600">Case ID</div>
                    <div className="text-sm font-medium text-gray-900">{anomaly.caseId}</div>
                  </div>
                )}
                <div>
                  <div className="text-xs text-gray-600">Assigned To</div>
                  <div className="text-sm font-medium text-gray-900">{anomaly.assignedTo || "Unassigned"}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-600">Review Status</div>
                  <StatusBadge status={anomaly.reviewStatus} />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Actions</h3>
              <div className="space-y-2">
                <button className="w-full px-3 py-2 text-white rounded-lg text-sm font-medium">
                  Assign to Me
                </button>
                <button className="w-full px-3 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium">
                  Create Case
                </button>
                <button className="w-full px-3 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium">
                  Export Report
                </button>
              </div>
            </div>

            {/* Timestamps */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Timestamps</h3>
              <div className="space-y-2">
                <div>
                  <div className="text-xs text-gray-600">Created</div>
                  <div className="text-xs text-gray-900">{format(new Date(anomaly.createdAt), "MMM dd, yyyy HH:mm")}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-600">Updated</div>
                  <div className="text-xs text-gray-900">{format(new Date(anomaly.updatedAt), "MMM dd, yyyy HH:mm")}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NarrativePage;
