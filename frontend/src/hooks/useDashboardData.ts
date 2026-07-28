import { useState, useEffect } from "react";
import { message } from "antd";
import anomalyService, { AnomalyStats } from "../services/anomaly/anomalyService";
import transactionService from "../services/transaction/transactionService";
import { AnomalyResult } from "../types/anomaly.types";

interface DashboardData {
  stats: AnomalyStats | null;
  recentAnomalies: AnomalyResult[];
  transactionCount: number;
  loading: boolean;
  error: Error | null;
}

export const useDashboardData = (): DashboardData => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [stats, setStats] = useState<AnomalyStats | null>(null);
  const [recentAnomalies, setRecentAnomalies] = useState<AnomalyResult[]>([]);
  const [transactionCount, setTransactionCount] = useState(0);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [statsData, anomaliesData, transactionsData] = await Promise.all([
          anomalyService.getStats(),
          anomalyService.listResults({ page: 1, page_size: 100 }),
          transactionService.list({ page: 1, page_size: 1 }),
        ]);

        setStats(statsData);
        setRecentAnomalies(anomaliesData.items || []);
        setTransactionCount(transactionsData.total || 0);
      } catch (err: any) {
        console.error("Failed to fetch dashboard data:", err);
        setError(err);
        message.error("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return {
    stats,
    recentAnomalies,
    transactionCount,
    loading,
    error,
  };
};
