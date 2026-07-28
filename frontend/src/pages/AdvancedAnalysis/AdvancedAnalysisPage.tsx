import React, { useState } from "react";

const ANALYSIS_URL = "https://blockchain-analytics-ui-1083336257191.us-central1.run.app/";

const AdvancedAnalysisPage: React.FC = () => {
  const [loading, setLoading] = useState(true);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 64px)", overflow: "hidden" }}>
      {/* Page header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-3 flex-shrink-0">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Advanced Analysis</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Blockchain analytics powered by external intelligence platform
          </p>
        </div>
        <a
          href={ANALYSIS_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-auto inline-flex items-center gap-1.5 text-xs text-gray-500 border border-gray-200 rounded px-2.5 py-1 transition-colors"
        >
          <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          Open in new tab
        </a>
      </div>

      {/* Loading overlay */}
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white z-10" style={{ top: 120 }}>
          <div className="flex flex-col items-center gap-3">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
            <span className="text-sm text-gray-500">Loading advanced analysis...</span>
          </div>
        </div>
      )}

      {/* Iframe */}
      <iframe
        src={ANALYSIS_URL}
        title="Advanced Analysis"
        onLoad={() => setLoading(false)}
        style={{
          flex: 1,
          width: "100%",
          border: "none",
          display: "block",
        }}
        allow="same-origin"
        sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
      />
    </div>
  );
};

export default AdvancedAnalysisPage;
