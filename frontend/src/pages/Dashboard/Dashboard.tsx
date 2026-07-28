import React from "react";
import { Row, Col, Spin } from "antd";
import { useDashboardData } from "../../hooks/useDashboardData";
import {
  transformAnomaliesOverTime,
  transformAnomaliesByCategory,
  transformRiskDistribution,
  getTopAlertedEntities,
  transformRecentAlerts,
} from "../../utils/dashboardUtils";
import StatisticsCards from "../../components/Dashboard/StatisticsCards";
import AnomaliesOverTimeChart from "../../components/Dashboard/AnomaliesOverTimeChart";
import AnomaliesByCategoryChart from "../../components/Dashboard/AnomaliesByCategoryChart";
import RiskScoreDistributionChart from "../../components/Dashboard/RiskScoreDistributionChart";
import RecentAlertsTable from "../../components/Dashboard/RecentAlertsTable";
import TopAlertedEntities from "../../components/Dashboard/TopAlertedEntities";

const Dashboard: React.FC = () => {
  const { stats, recentAnomalies, transactionCount, loading } = useDashboardData();

  // Transform data for charts
  const anomaliesOverTimeData = transformAnomaliesOverTime(recentAnomalies);
  const anomaliesByCategoryData = transformAnomaliesByCategory(recentAnomalies);
  const riskScoreData = transformRiskDistribution(stats);
  const topEntitiesData = getTopAlertedEntities(recentAnomalies);
  const recentAlertsData = transformRecentAlerts(recentAnomalies);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "60vh" }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: "24px", background: "#f5f5f5", minHeight: "100vh" }}>
      {/* Top Statistics Cards */}
      <StatisticsCards stats={stats} transactionCount={transactionCount} />

      {/* Charts Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={10}>
          <AnomaliesOverTimeChart data={anomaliesOverTimeData} />
        </Col>
        <Col xs={24} lg={7}>
          <AnomaliesByCategoryChart data={anomaliesByCategoryData} total={stats?.total_anomalies || 0} />
        </Col>
        <Col xs={24} lg={7}>
          <RiskScoreDistributionChart data={riskScoreData} total={stats?.total_anomalies || 0} />
        </Col>
      </Row>

      {/* Bottom Row */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <RecentAlertsTable data={recentAlertsData} />
        </Col>
        <Col xs={24} lg={8}>
          <TopAlertedEntities data={topEntitiesData} />
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
