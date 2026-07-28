import { AnomalyResult } from "../types/anomaly.types";
import { AnomalyStats } from "../services/anomaly/anomalyService";

export interface TimeSeriesData {
  date: string;
  anomalies: number;
}

export interface CategoryData {
  name: string;
  value: number;
  percentage: number;
}

export interface RiskDistributionData {
  name: string;
  value: number;
  count: string;
  percentage: string;
}

export interface TopEntity {
  name: string;
  count: number;
}

export interface AlertTableData {
  key: string;
  alertId: string;
  time: string;
  entity: string;
  type: string;
  riskScore: number;
  status: string;
  transactionId: string;
}

/**
 * Transform anomalies into time series data for charts
 */
export const transformAnomaliesOverTime = (
  anomalies: AnomalyResult[]
): TimeSeriesData[] => {
  if (!anomalies.length) return [];

  const dateMap = new Map<string, number>();
  anomalies.forEach((anomaly) => {
    const date = new Date(anomaly.createdAt).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
    dateMap.set(date, (dateMap.get(date) || 0) + 1);
  });

  return Array.from(dateMap.entries())
    .map(([date, count]) => ({ date, anomalies: count }))
    .slice(-7); // Last 7 days
};

/**
 * Transform anomalies by category for pie chart
 */
export const transformAnomaliesByCategory = (
  anomalies: AnomalyResult[]
): CategoryData[] => {
  if (!anomalies.length) return [];

  const categoryMap = new Map<string, number>();
  anomalies.forEach((anomaly) => {
    const category = anomaly.anomalyCategory || "Other";
    categoryMap.set(category, (categoryMap.get(category) || 0) + 1);
  });

  const total = anomalies.length;
  return Array.from(categoryMap.entries())
    .map(([name, value]) => ({
      name,
      value,
      percentage: Math.round((value / total) * 100),
    }))
    .sort((a, b) => b.value - a.value);
};

/**
 * Transform stats into risk distribution data
 */
export const transformRiskDistribution = (
  stats: AnomalyStats | null
): RiskDistributionData[] => {
  if (!stats) return [];

  const total = stats.total_anomalies || 1;
  return [
    {
      name: "Critical",
      value: stats.critical || 0,
      count: `${stats.critical || 0}`,
      percentage: (((stats.critical || 0) / total) * 100).toFixed(1),
    },
    {
      name: "High",
      value: stats.high || 0,
      count: `${stats.high || 0}`,
      percentage: (((stats.high || 0) / total) * 100).toFixed(1),
    },
    {
      name: "Medium",
      value: stats.medium || 0,
      count: `${stats.medium || 0}`,
      percentage: (((stats.medium || 0) / total) * 100).toFixed(1),
    },
    {
      name: "Low",
      value: stats.low || 0,
      count: `${stats.low || 0}`,
      percentage: (((stats.low || 0) / total) * 100).toFixed(1),
    },
  ];
};

/**
 * Get top alerted entities from anomalies
 */
export const getTopAlertedEntities = (
  anomalies: AnomalyResult[]
): TopEntity[] => {
  if (!anomalies.length) return [];

  const entityMap = new Map<string, number>();
  anomalies.forEach((anomaly) => {
    const entity = anomaly.caseId || anomaly.fromAccount || "Unknown";
    entityMap.set(entity, (entityMap.get(entity) || 0) + 1);
  });

  return Array.from(entityMap.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);
};

/**
 * Transform anomalies for alert table
 */
export const transformRecentAlerts = (
  anomalies: AnomalyResult[]
): AlertTableData[] => {
  return anomalies.slice(0, 5).map((anomaly, idx) => ({
    key: idx.toString(),
    alertId: anomaly.anomalyId,
    time: new Date(anomaly.createdAt).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }),
    entity: anomaly.clientId || anomaly.fromAccount || "Unknown",
    type: anomaly.anomalyCategory || "Unknown",
    riskScore: Math.round(anomaly.anomalyScore * 100),
    status:
      anomaly.reviewStatus === "PENDING"
        ? "New"
        : anomaly.reviewStatus === "UNDER_REVIEW"
        ? "In Review"
        : "Assigned",
    transactionId: anomaly.transactionHash,
  }));
};

/**
 * Map review status to display label
 */
export const getStatusLabel = (status: string): string => {
  const statusMap: Record<string, string> = {
    PENDING: "New",
    UNDER_REVIEW: "In Review",
    APPROVED: "Approved",
    REJECTED: "Rejected",
  };
  return statusMap[status] || "Assigned";
};

/**
 * Get color based on risk score
 */
export const getRiskScoreColor = (score: number): string => {
  if (score >= 90) return "red";
  if (score >= 70) return "orange";
  return "gold";
};

/**
 * Get color based on status
 */
export const getStatusColor = (status: string): string => {
  if (status === "New") return "red";
  if (status === "In Review") return "orange";
  return "blue";
};
