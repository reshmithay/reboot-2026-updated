import apiClient from "../../clients/api/axiosClient";
import { AnomalyResult, AnomalyResultListResponse } from "../../types/anomaly.types";

export interface BulkDetectRowResult {
  transaction_hash: string;
  anomaly_id: string | null;
  is_anomaly: boolean;
  anomaly_score: number | null;
  severity: string | null;
}

export interface BulkDetectError {
  transaction_hash: string;
  error: string;
}

export interface BulkDetectResponse {
  status: string;
  total: number;
  anomalies_found: number;
  clean: number;
  error_count: number;
  errors: BulkDetectError[];
  results: BulkDetectRowResult[];
}

export interface Anomaly {
  id: string;
  transaction_id: string;
  score: number;
  severity: "low" | "medium" | "high" | "critical";
  status: "pending" | "confirmed" | "false_positive" | "under_review";
  features: Record<string, unknown>;
  detected_at: string;
  blockchain_tx_hash?: string;
  narrative_id?: string;
}

export interface AnomalyStats {
  total_anomalies: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  under_review: number;
  pending: number;
  approved: number;
  rejected: number;
  avg_anomaly_score: number;
  by_severity?: Record<string, number>;
  by_review_status?: Record<string, number>;
}

export interface AnomalyDetectRequest {
  transaction_hash: string;
  force?: boolean;
}

export interface AnomalyListParams {
  page?: number;
  page_size?: number;
  severity?: string;
  review_status?: string;
  anomaly_category?: string;
  client_id?: string;
  start_date?: string; // ISO date string for filtering by created_at
  end_date?: string;   // ISO date string for filtering by created_at
}

const anomalyService = {
  /**
   * Detect anomaly for a transaction by hash
   */
  detect: (transactionHash: string, force: boolean = false): Promise<AnomalyResult> =>
    apiClient
      .post("/api/v1/anomalies/detect", { transaction_hash: transactionHash, force })
      .then((r) => r.data),

  /**
   * List anomaly results with filters and pagination
   */
  listResults: (params?: AnomalyListParams): Promise<AnomalyResultListResponse> =>
    apiClient
      .get("/api/v1/anomalies/results/", { params })
      .then((r) => r.data),

  /**
   * Get anomaly result by ID
   */
  getResult: (anomalyId: string): Promise<AnomalyResult> =>
    apiClient
      .get(`/api/v1/anomalies/results/${anomalyId}`)
      .then((r) => r.data),

  /**
   * Get anomaly result by transaction ID
   */
  getByTransactionId: (transactionId: string): Promise<AnomalyResult> =>
    apiClient
      .get(`/api/v1/anomalies/results/transaction/${transactionId}`)
      .then((r) => r.data),

  /**
   * Legacy: List anomalies
   */
  list: (params?: {
    page?: number;
    page_size?: number;
    severity?: string;
  }) =>
    apiClient.get("/api/v1/anomalies/", { params }).then((r) => r.data),

  /**
   * Legacy: Get anomaly by ID
   */
  get: (anomalyId: string): Promise<Anomaly> =>
    apiClient.get(`/api/v1/anomalies/${anomalyId}`).then((r) => r.data),

  /**
   * Get anomaly statistics summary
   */
  getStats: (): Promise<AnomalyStats> =>
    apiClient.get("/api/v1/anomalies/stats/summary").then((r) => r.data),

  /**
   * Bulk detect anomalies from a CSV file.
   * The CSV must contain a 'transaction_hash' column.
   */
  bulkDetect: (file: File): Promise<BulkDetectResponse> => {
    const form = new FormData();
    form.append("file", file);
    return apiClient
      .post("/api/v1/anomalies/detect/bulk", form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
};

export default anomalyService;
