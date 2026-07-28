import React from "react";
import { Card, Row, Col, Statistic } from "antd";
import {
  ThunderboltOutlined,
  WarningOutlined,
  AlertOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons";
import { AnomalyStats } from "../../services/anomaly/anomalyService";
import { CHART_COLORS, BACKGROUND_COLORS } from "../../constants/dashboardConstants";

interface StatisticsCardsProps {
  stats: AnomalyStats | null;
  transactionCount: number;
}

interface StatCardConfig {
  title: string;
  value: number;
  icon: React.ReactNode;
  iconColor: string;
  iconBg: string;
  trendText: string;
  trendColor: string;
}

const StatisticsCards: React.FC<StatisticsCardsProps> = ({ stats, transactionCount }) => {
  const statCards: StatCardConfig[] = [
    {
      title: "Total Transactions",
      value: transactionCount,
      icon: <ThunderboltOutlined style={{ fontSize: 24, color: CHART_COLORS.primary }} />,
      iconColor: CHART_COLORS.primary,
      iconBg: BACKGROUND_COLORS.primary,
      trendText: "Live data",
      trendColor: CHART_COLORS.success,
    },
    {
      title: "Anomalies Detected",
      value: stats?.total_anomalies || 0,
      icon: <WarningOutlined style={{ fontSize: 24, color: CHART_COLORS.danger }} />,
      iconColor: CHART_COLORS.danger,
      iconBg: BACKGROUND_COLORS.danger,
      trendText: "Total detected",
      trendColor: CHART_COLORS.danger,
    },
    {
      title: "High Risk Alerts",
      value: (stats?.critical || 0) + (stats?.high || 0),
      icon: <AlertOutlined style={{ fontSize: 24, color: CHART_COLORS.warning }} />,
      iconColor: CHART_COLORS.warning,
      iconBg: BACKGROUND_COLORS.warning,
      trendText: "Critical + High",
      trendColor: "#ff7a45",
    },
    {
      title: "Resolved Alerts",
      value: stats?.approved || 0,
      icon: <CheckCircleOutlined style={{ fontSize: 24, color: CHART_COLORS.success }} />,
      iconColor: CHART_COLORS.success,
      iconBg: BACKGROUND_COLORS.success,
      trendText: "Approved",
      trendColor: CHART_COLORS.success,
    },
    // {
    //   title: "Under Review",
    //   value: stats?.under_review || 0,
    //   icon: <UserOutlined style={{ fontSize: 24, color: CHART_COLORS.info }} />,
    //   iconColor: CHART_COLORS.info,
    //   iconBg: BACKGROUND_COLORS.info,
    //   trendText: "In Progress",
    //   trendColor: CHART_COLORS.info,
    // },
  ];

  return (
    <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
      {statCards.map((card, index) => (
        <Col xs={24} sm={12} lg={4.8} key={index}>
          <Card bordered={false}>
            <Statistic
              title={card.title}
              value={card.value}
              prefix={
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 12,
                    background: card.iconBg,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: 8,
                  }}
                >
                  {card.icon}
                </div>
              }
              valueStyle={{ fontSize: 28, fontWeight: 700, marginTop: 8 }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: card.trendColor }}>
              {card.trendText}
            </div>
          </Card>
        </Col>
      ))}
    </Row>
  );
};

export default StatisticsCards;
