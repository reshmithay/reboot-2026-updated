import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import { InfoCard, DataCard } from "../../components/Common/Cards";
import { RiskBadge } from "../../components/Common/Badges";
import { ClientRegistry, ClientProfileStats, RiskDistribution } from "../../types/client.types";
import { AnomalyResult } from "../../types/anomaly.types";
import clientService from "../../services/client/clientService";
import anomalyService from "../../services/anomaly/anomalyService";

const ClientProfilePage: React.FC = () => {
  const { clientId } = useParams<{ clientId: string }>();
  const [client, setClient] = useState<ClientRegistry | null>(null);
  const [recentAlerts, setRecentAlerts] = useState<AnomalyResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch client data and recent alerts
  useEffect(() => {
    const fetchData = async () => {
      if (!clientId) return;
      
      try {
        setLoading(true);
        setError(null);
        
        // Fetch client data
        const clientData = await clientService.get(clientId);
        setClient(clientData);
        
        // Fetch recent alerts for this client
        try {
          const alertsResponse = await anomalyService.listResults({
            client_id: clientId,
            page: 1,
            page_size: 5,
          });
          setRecentAlerts(alertsResponse.items);
        } catch (alertErr) {
          console.warn("Failed to fetch alerts:", alertErr);
          // Don't fail the whole page if alerts fail to load
          setRecentAlerts([]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch client");
        console.error("Failed to fetch client:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [clientId]);

  // Mock profile stats (TODO: fetch from API when endpoint is available)
  const profileStats: ClientProfileStats = {
    total_addresses: 3,
    balance: 1000,
    total_inflow: 321497215.84,
    total_outflow: 322890695.93,
    total_transaction: 4,
    total_value: 479052.7,
    total_deposit: 478854.87,
    total_withdraw: 197.83,
    unresolved_alerts: 12,
  };

  // Risk distribution data (TODO: fetch from API when endpoint is available)
  const riskDistributionData: RiskDistribution = {
    critical: 15,
    high: 25,
    medium: 30,
    low: 20,
    no_risk: 8,
    info: 2,
  };

  // Prepare chart data
  const pieChartData = [
    { name: "Critical", value: riskDistributionData.critical, color: "#DC2626" },
    { name: "High", value: riskDistributionData.high, color: "#F97316" },
    { name: "Medium", value: riskDistributionData.medium, color: "#FACC15" },
    { name: "Low", value: riskDistributionData.low, color: "#22C55E" },
    { name: "No Risk", value: riskDistributionData.no_risk, color: "#86EFAC" },
    { name: "Info", value: riskDistributionData.info, color: "#D1D5DB" },
  ];

  // Risk engine data for bar chart
  const riskEngineData = [
    { name: "Forensics Analysis", value: 3 },
    { name: "AML Sanctions", value: 3 },
    { name: "Trace API (Heuristic)", value: 2 },
    { name: "Abuse Identification", value: 3 },
    { name: "Sanctions Identification", value: 3 },
    { name: "AML", value: 2 },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-sm text-gray-600">Loading client profile...</p>
        </div>
      </div>
    );
  }

  if (error || !client) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <div className="flex items-center gap-2">
            <svg className="h-5 w-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm text-red-800">{error || "Client not found"}</span>
          </div>
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
              <h1 className="text-2xl font-bold text-gray-900">
                Unified Customer Entity Profile
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                A 360° view of customer risk in one place.
              </p>
            </div>
            <button className="text-white hidden px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
              Upgrade to Unlock
            </button>
          </div>
          <div className="mt-4 text-sm text-gray-600">
            Connect all addresses and transactions to a single entity. Build a clear{" "}
            <span className="font-medium">risk profile</span> to support enhanced due
            diligence and confident decisions.
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Client Info Card */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {client.client_name}
              </h2>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>Client ID: {client.client_id}</span>
                <span>•</span>
                <span>Type: {client.client_type || "N/A"}</span>
                <span>•</span>
                <RiskBadge severity={client.risk_tier || "LOW"} />
              </div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid hidden grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 p-6 bg-orange-50 border-2 border-orange-200 rounded-lg">
            <DataCard
              label="Total Address"
              value={profileStats.total_addresses}
              className="text-center"
            />
            <DataCard
              label="Balance"
              value={`$${profileStats.balance.toLocaleString()}`}
              className="text-center"
            />
            <DataCard
              label="Total Inflow"
              value={`$${(profileStats.total_inflow / 1000000).toFixed(1)}M`}
              subValue={`${profileStats.total_inflow.toLocaleString()}`}
              className="text-center"
            />
            <DataCard
              label="Total Outflow"
              value={`$${(profileStats.total_outflow / 1000000).toFixed(1)}M`}
              subValue={`${profileStats.total_outflow.toLocaleString()}`}
              className="text-center"
            />
            <DataCard
              label="Total Transaction"
              value={profileStats.total_transaction}
              className="text-center"
            />
            <DataCard
              label="Total Value"
              value={`$${profileStats.total_value.toLocaleString()}`}
              className="text-center"
            />
            <DataCard
              label="Total Deposit"
              value={`$${profileStats.total_deposit.toLocaleString()}`}
              className="text-center"
            />
            <DataCard
              label="Total Withdraw"
              value={`$${profileStats.total_withdraw.toLocaleString()}`}
              className="text-center"
            />
          </div>
        </div>

        {/* Charts and Alerts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Risk Engine Chart */}
          <div className="lg:col-span-1">
            <InfoCard title="Triggered Risk Engine">
              <div className="mb-4 text-sm text-gray-600">
                Unresolved Alerts: <span className="font-semibold">12</span>
              </div>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={riskEngineData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </InfoCard>
          </div>

          {/* Risk Distribution Pie Chart */}
          <div className="lg:col-span-1">
            <InfoCard title="Risk Distribution">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {pieChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Legend
                    verticalAlign="bottom"
                    height={36}
                    iconType="circle"
                    formatter={(value, entry: any) => (
                      <span className="text-xs text-gray-700">
                        {value} ({entry.payload.value})
                      </span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            </InfoCard>
          </div>

          {/* Recent Alerts */}
          <div className="lg:col-span-1">
            <InfoCard
              title="Alerts"
              action={
                <a
                  href="#"
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  Alert Hub →
                </a>
              }
            >
              <div className="space-y-3">
                {recentAlerts.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 text-sm">
                    No recent alerts found
                  </div>
                ) : (
                  recentAlerts.map((alert) => (
                    <div
                      key={alert.anomalyId}
                      className="p-3 border border-gray-200 rounded-lg hover:shadow-sm transition-shadow cursor-pointer"
                      onClick={() => window.location.href = `/narrative/${alert.transactionId}`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="text-xs text-gray-500">
                          {new Date(alert.detectedAt).toLocaleString()}
                        </div>
                        <RiskBadge severity={alert.severity} />
                      </div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-medium text-gray-700">
                          {alert.anomalyCategory}
                        </span>
                        <span className="text-xs text-gray-500">
                          Score: {(alert.anomalyScore * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="text-sm text-gray-900 mb-2">
                        {alert.anomalyReasons && alert.anomalyReasons.length > 0
                          ? alert.anomalyReasons[0].description.length > 60
                            ? alert.anomalyReasons[0].description.substring(0, 60) + "..."
                            : alert.anomalyReasons[0].description
                          : "Anomaly detected"}
                      </div>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>Status: {alert.reviewStatus}</span>
                        <span>{alert.assignedTo ? `Assigned to: ${alert.assignedTo}` : "Unassigned"}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </InfoCard>
          </div>
        </div>

        {/* Client Details Section */}
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Basic Information */}
          <InfoCard title="Client Information">
            <div className="grid grid-cols-2 gap-4">
              <DataCard label="LEI" value={client.lei || "N/A"} />
              <DataCard
                label="Industry Sector"
                value={client.industry_sector || "N/A"}
              />
              <DataCard
                label="Country"
                value={client.country_of_incorporation || "N/A"}
              />
              <DataCard
                label="Relationship Manager"
                value={client.relationship_manager || "N/A"}
              />
              <DataCard
                label="KYC Status"
                value={client.kyc_status || "N/A"}
              />
              <DataCard
                label="AML Status"
                value={client.aml_status || "N/A"}
              />
            </div>
          </InfoCard>

          {/* Limits and Facility */}
          <InfoCard title="Limits & Facility">
            <div className="grid grid-cols-2 gap-4">
              <DataCard
                label="Credit Limit"
                value={`₹${client.credit_limit.toLocaleString()}`}
              />
              <DataCard
                label="Facility Type"
                value={client.facility_type || "N/A"}
              />
              <DataCard
                label="Daily Deposit Limit"
                value={`₹${client.daily_deposit_limit.toLocaleString()}`}
              />
              <DataCard
                label="Daily Withdrawal Limit"
                value={`₹${client.daily_withdrawal_limit.toLocaleString()}`}
              />
              <DataCard
                label="Risk tier"
                value={client.risk_tier || "N/A"}
              />
              <DataCard
                label="Expected Activity"
                value={client.expected_activity_window || "N/A"}
              />
            </div>
          </InfoCard>
        </div>
      </div>
    </div>
  );
};

export default ClientProfilePage;
