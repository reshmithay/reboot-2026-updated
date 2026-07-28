import apiClient from "../../clients/api/axiosClient";

export interface Narrative {
  id: string;
  anomaly_id: string;
  narrative_type: string;
  title: string;
  summary: string;
  detailed_explanation: string;
  risk_factors: string[];
  recommendations: string[];
  confidence_score: number;
  generated_at: string;
  model_used: string;
}

export interface ShapContributor {
  feature: string;
  actual_value: number;
  shap_contribution: number;
  direction: string;
}

export interface ShapFeaturesResponse {
  anomaly_id: string;
  transaction_hash: string;
  prediction_probability: number;
  prediction_label: string;
  shap_contributors: ShapContributor[];
  anomaly_score: number;
  anomaly_category: string;
}

export interface NarrativeResponse {
  anomaly_id: string;
  narrative: string;
  shap_contributors: ShapContributor[];
  prediction_probability: number;
  prediction_label: string;
  model_used: string;
  generated_at: string;
}

export interface NarrativeGenerateRequest {
  anomaly_id: string;
  top_k?: number;
  persona?: string;
}

const narrativeService = {
  generate: (
    anomalyId: string,
    options?: {
      narrative_type?: string;
      include_recommendations?: boolean;
      audience?: string;
    }
  ): Promise<Narrative> =>
    apiClient
      .post("/api/v1/narratives/generate", {
        anomaly_id: anomalyId,
        ...options,
      })
      .then((r) => r.data),

  getByAnomalyId: (anomalyId: string): Promise<Narrative> =>
    apiClient.get(`/api/v1/narratives/${anomalyId}`).then((r) => r.data),

  /**
   * Get SHAP feature contributions for an anomaly (from backend)
   */
  getShapFeatures: (
    anomalyId: string,
    topK: number = 5
  ): Promise<ShapFeaturesResponse> =>
    apiClient
      .get(`/api/v1/anomalies/shap/${anomalyId}`, { params: { top_k: topK } })
      .then((r) => r.data),

  /**
   * Generate AI narrative using SHAP + Cortex (from backend)
   */
  generateShapNarrative: (
    request: NarrativeGenerateRequest
  ): Promise<NarrativeResponse> =>
    apiClient
      .post(`/api/v1/anomalies/narrative/generate`, request)
      .then((r) => r.data),
};

export default narrativeService;
