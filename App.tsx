import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ConfigProvider } from "antd";
import { MainLayout } from "./layouts/MainLayout";
// New UI Pages
import TransactionListPage from "./pages/Transactions/TransactionListPage";
import ClientListPage from "./pages/Clients/ClientListPage";
import ClientProfilePage from "./pages/Clients/ClientProfilePage";
import AnomalyListPage from "./pages/Anomalies/AnomalyListPage";
import BulkScreeningPage from "./pages/Anomalies/BulkScreeningPage";
// import AnomalyNarrativePage from "./pages/Narrative/AnomalyNarrativePage"; // Old component with hardcoded data

// Original Pages (if still needed)
import Dashboard from "./pages/Dashboard/Dashboard";
import Transactions from "./pages/Transactions/Transactions";
import Anomalies from "./pages/Anomalies/Anomalies";
import Narrative from "./pages/Narrative/Narrative";
import AnomalyNarrativePage from "./pages/Narrative/AnomalyNarrativePage";
import ComplianceDashboard from "./pages/Compliance/ComplianceDashboard";
import AdvancedAnalysisPage from "./pages/AdvancedAnalysis/AdvancedAnalysisPage";

const App: React.FC = () => {
  return (
    <ConfigProvider
      theme={{
        components: {
          Layout: { headerBg: "#003366", siderBg: "#001529" },
          Menu: { itemSelectedBg: "#006a4d", itemSelectedColor: "#ffffff" },
        },
        token: {
          colorPrimary: "#2563eb",
          colorSuccess: "#10a870",
          colorWarning: "#e66d00",
          colorError: "#db0f30",
          borderRadius: 8,
        },
      }}
    >
      <BrowserRouter>
        <MainLayout>
          <Routes>
            {/* Main Compliance Dashboard as Home */}
            <Route path="/" element={<ComplianceDashboard />} />
            <Route path="/compliance" element={<ComplianceDashboard />} />

            {/* Transaction Routes */}
            <Route path="/transactions" element={<TransactionListPage />} />

            {/* Client Routes */}
            <Route path="/clients" element={<ClientListPage />} />
            <Route path="/clients/:clientId" element={<ClientProfilePage />} />

            {/* Anomaly Routes */}
            <Route path="/anomalies" element={<AnomalyListPage />} />
            <Route path="/bulk-screening" element={<BulkScreeningPage />} />
            <Route
              path="/narrative/:transactionId"
              element={<AnomalyNarrativePage />}
            />

            {/* Original Dashboard & Pages */}
            <Route path="/dashboard" element={<Dashboard />} />
            <Route
              path="/advanced-analysis"
              element={<AdvancedAnalysisPage />}
            />
            <Route path="/transactions-old" element={<Transactions />} />
            <Route path="/anomalies-old" element={<Anomalies />} />
            {/* Old narrative with hardcoded data - commented out */}
            <Route path="/narrative-old/:anomalyId" element={<Narrative />} />
          </Routes>
        </MainLayout>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;
