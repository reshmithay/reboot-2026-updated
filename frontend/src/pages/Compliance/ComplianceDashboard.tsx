import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { RiskBadge } from "../../components/Common/Badges";
import { InfoCard, DataCard } from "../../components/Common/Cards";
import { BulkScreeningModal } from "../../components/Common/Modal";
import { mockAnomalies } from "../../utilities/mockData";
import anomalyService from "../../services/anomaly/anomalyService";
import { message } from "antd";

interface TransactionAnalysis {
  transactionHash: string;
  riskScore: number;
  severity: string;
  amount: number;
  currency: string;
  from: string;
  to: string;
  timestamp: string;
  anomalyReasons: string[];
  recommendation: string;
}

const ComplianceDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [isBulkModalOpen, setIsBulkModalOpen] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<TransactionAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);


  const handleAnalyze = async () => {
    if (!searchQuery.trim()) {
      message.warning("Please enter a transaction hash to analyze");
      return;
    }

    setIsAnalyzing(true);
    setAnalysisResult(null);

    try {
      // Call anomaly detection API
      const result = await anomalyService.detect(searchQuery.trim(), false);

      // Map API response to TransactionAnalysis interface
      const analysis: TransactionAnalysis = {
        transactionHash: result.transactionHash,
        riskScore: result.anomalyScore * 100,
        severity: result.severity,
        amount: result.amount || 0,
        currency: result.currency || "INR",
        from: result.fromWalletAddress || result.fromAccount || "Unknown",
        to: result.toWalletAddress || result.toAccount || "Unknown",
        timestamp: result.detectedAt,
        anomalyReasons: result.anomalyReasons.map(r => r.description),
        recommendation: result.anomalyScore > 0.7 
          ? "High risk transaction - Recommend further investigation and possible hold"
          : result.anomalyScore > 0.4
          ? "Medium risk - Monitor transaction closely"
          : "Low risk - No immediate action required",
      };

      setAnalysisResult(analysis);
      message.success("Transaction analysis completed successfully");
    } catch (error: any) {
      console.error("Failed to analyze transaction:", error);
      const errorMessage = error.response?.data?.detail || error.message || "Failed to analyze transaction";
      message.error(errorMessage);
      setAnalysisResult(null);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleBulkScreen = (file: File) => {
    console.log("Screening file:", file.name);
    // Implement bulk screening logic here
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Welcome to Blockchain Anomaly AI
            </h1>
            <p className="text-sm text-gray-600">
              Screen transactions and addresses for AML/CFT risk analysis
            </p>
          </div>

          {/* Search Section */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Screen Address or Transaction for AML/CFT Risk
            </h2>
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg
                    className="h-5 w-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </div>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2  sm:text-sm"
                  placeholder="Enter transaction hash or wallet address..."
                />
              </div>
             
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="inline-flex items-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white  focus:outline-none focus:ring-2 focus:ring-offset-2  disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAnalyzing ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                    Analyze
                  </>
                )}
              </button>
              <button
                onClick={() => setIsBulkModalOpen(true)}
                className="inline-flex items-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm text-sm font-medium"
              >
                <svg
                  className="h-5 w-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                Upload CSV
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Analysis Results */}
        {analysisResult && (
          <div className="mb-8">
            <InfoCard title="Transaction Analysis Results">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column - Transaction Details */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Transaction Details</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <DataCard label="Transaction Hash" value={analysisResult.transactionHash.substring(0, 20) + "..."} />
                      <DataCard label="Amount" value={`${analysisResult.currency} ${(analysisResult.amount || 0).toLocaleString()}`} />
                      <DataCard label="From" value={analysisResult.from.substring(0, 15) + "..."} />
                      <DataCard label="To" value={analysisResult.to.substring(0, 15) + "..."} />
                      <DataCard label="Timestamp" value={new Date(analysisResult.timestamp).toLocaleString()} />
                      <div className="flex flex-col">
                        <span className="text-sm text-gray-500 mb-1">Risk Level</span>
                        <RiskBadge severity={analysisResult.severity} />
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Anomaly Reasons</h3>
                    <ul className="space-y-2">
                      {analysisResult.anomalyReasons.map((reason, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                          <svg className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className={`rounded-lg p-4 ${analysisResult.riskScore > 70 ? 'bg-red-50 border border-red-200' : 'bg-yellow-50 border border-yellow-200'}`}>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Recommendation</h3>
                    <p className="text-sm text-gray-700">{analysisResult.recommendation}</p>
                  </div>
                </div>

                {/* Right Column - Risk Score */}
                <div className="space-y-4">
                  <div className="bg-white border-2 border-gray-200 rounded-lg p-6 text-center">
                    <div className="text-sm font-medium text-gray-600 mb-2">Risk Score</div>
                    <div className={`text-5xl font-bold mb-2 ${
                      analysisResult.riskScore > 70 ? 'text-red-600' : 
                      analysisResult.riskScore > 40 ? 'text-orange-600' : 
                      'text-green-600'
                    }`}>
                      {analysisResult.riskScore.toFixed(0)}%
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full ${
                          analysisResult.riskScore > 70 ? 'bg-red-600' : 
                          analysisResult.riskScore > 40 ? 'bg-orange-600' : 
                          'bg-green-600'
                        }`}
                        style={{ width: `${analysisResult.riskScore}%` }}
                      />
                    </div>
                  </div>

                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Actions</h3>
                    <div className="space-y-2">
                      <button 
                        onClick={() => analysisResult?.transactionHash && navigate(`/narrative/${analysisResult.transactionHash}`)}
                        disabled={!analysisResult?.transactionHash}
                        className="w-full text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        View Full Report
                      </button>
                      <button className="w-full text-gray-700 border border-gray-300 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                        Add to Watchlist
                      </button>
                      <button className="w-full text-red-600 border border-red-300 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                        Flag Transaction
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </InfoCard>
          </div>
        )}

        {/* Recent Anomalies Section */}
        <div className="mt-8">
          <InfoCard
            title="Recent Anomaly Detections"
            action={
              <a
                href="/anomalies"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                View all →
              </a>
            }
          >
            <div className="space-y-3">
              {mockAnomalies.slice(0, 3).map((anomaly) => (
                <div
                  key={anomaly.anomalyId}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:shadow-sm transition-shadow cursor-pointer"
                  onClick={() => navigate(`/narrative/${anomaly.transactionId}`)}
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-mono text-gray-600">
                        {anomaly.transactionHash.substring(0, 20)}...
                      </span>
                      <RiskBadge severity={anomaly.severity} />
                    </div>
                    <div className="text-sm text-gray-600">
                      {anomaly.anomalyReasons[0]?.description}
                    </div>
                  </div>
                  <div className="text-right ml-4">
                    <div className="text-lg font-semibold text-gray-900">
                      {(anomaly.anomalyScore * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-500">Risk Score</div>
                  </div>
                </div>
              ))}
            </div>
          </InfoCard>
        </div>
      </div>

      {/* Bulk Screening Modal */}
      <BulkScreeningModal
        isOpen={isBulkModalOpen}
        onClose={() => setIsBulkModalOpen(false)}
        onScreen={handleBulkScreen}
      />
    </div>
  );
};

export default ComplianceDashboard;
