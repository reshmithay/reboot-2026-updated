export enum AnomalyStatus {
  PENDING = "PENDING",
  APPROVED = "APPROVED",
  REJECTED = "REJECTED",
  FALSE_POSITIVE = "FALSE_POSITIVE",
  UNDER_REVIEW = "UNDER_REVIEW",
}

export enum AnomalySeverity {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export enum AnomalyCategory {
  FRAUD = "FRAUD",
  RISK = "RISK",
  COMPLIANCE = "COMPLIANCE",
  OPERATIONAL = "OPERATIONAL",
  SUSPICIOUS = "SUSPICIOUS",
}

export interface AnomalyReason {
  reasonCode: string;
  description: string;
}

export interface AnomalyResult {
  anomalyId: string;
  transactionId: string;
  transactionHash: string;
  clientId?: string | null;
  
  // Transaction details
  amount?: number | null;
  currency?: string | null;
  fromAccount?: string | null;
  toAccount?: string | null;
  fromWalletAddress?: string | null;
  toWalletAddress?: string | null;
  transactionType?: string | null;
  
  // Anomaly detection results
  anomalyScore: number;
  severity: string;
  anomalyCategory: string;
  anomalyTypes: string[];
  anomalyReasons: AnomalyReason[];
  confidence: number;
  
  // Model information
  modelName?: string | null;
  modelVersion?: string | null;
  
  // Review and case management
  reviewStatus: string;
  assignedTo?: string | null;
  caseId?: string | null;
  
  // Timestamps
  detectedAt: string;
  createdAt: string;
  updatedAt: string;
}

export interface AnomalyResultListResponse {
  items: AnomalyResult[];
  total: number;
  page: number;
  page_size: number;
}
