-- PostgreSQL schema for anomaly_results table

CREATE TABLE IF NOT EXISTS anomaly_results (
    anomaly_id VARCHAR PRIMARY KEY,
    
    -- Transaction references
    transaction_id VARCHAR NOT NULL,
    transaction_hash VARCHAR NOT NULL,
    client_id VARCHAR,
    
    -- Transaction details (denormalized for reporting)
    amount DECIMAL(20, 2),
    currency VARCHAR,
    from_account VARCHAR,
    to_account VARCHAR,
    from_wallet_address VARCHAR,
    to_wallet_address VARCHAR,
    transaction_type VARCHAR,
    
    -- Anomaly detection results
    anomaly_score FLOAT NOT NULL,
    severity VARCHAR NOT NULL,
    anomaly_category VARCHAR NOT NULL,
    anomaly_types JSONB NOT NULL,
    anomaly_reasons JSONB NOT NULL,
    confidence FLOAT NOT NULL,
    
    -- Model information
    model_name VARCHAR,
    model_version VARCHAR,
    
    -- Review and case management
    review_status VARCHAR NOT NULL DEFAULT 'PENDING',
    assigned_to VARCHAR,
    case_id VARCHAR,
    
    -- Timestamps
    detected_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_anomaly_results_transaction_id ON anomaly_results(transaction_id);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_transaction_hash ON anomaly_results(transaction_hash);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_client_id ON anomaly_results(client_id);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_severity ON anomaly_results(severity);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_category ON anomaly_results(anomaly_category);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_review_status ON anomaly_results(review_status);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_detected_at ON anomaly_results(detected_at);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_score ON anomaly_results(anomaly_score);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_assigned_to ON anomaly_results(assigned_to);
CREATE INDEX IF NOT EXISTS idx_anomaly_results_case_id ON anomaly_results(case_id);

-- BigQuery equivalent schema
/*
CREATE TABLE IF NOT EXISTS `project.dataset.anomaly_results` (
    anomalyId STRING,
    transactionId STRING NOT NULL,
    transactionHash STRING NOT NULL,
    clientId STRING,
    amount NUMERIC,
    currency STRING,
    fromAccount STRING,
    toAccount STRING,
    fromWalletAddress STRING,
    toWalletAddress STRING,
    transactionType STRING,
    anomalyScore FLOAT64 NOT NULL,
    severity STRING NOT NULL,
    anomalyCategory STRING NOT NULL,
    anomalyTypes ARRAY<STRING> NOT NULL,
    anomalyReasons ARRAY<STRUCT<reasonCode STRING, description STRING>> NOT NULL,
    confidence FLOAT64 NOT NULL,
    modelName STRING,
    modelVersion STRING,
    reviewStatus STRING NOT NULL,
    assignedTo STRING,
    caseId STRING,
    detectedAt TIMESTAMP NOT NULL,
    createdAt TIMESTAMP NOT NULL,
    updatedAt TIMESTAMP NOT NULL
)
PARTITION BY DATE(detectedAt)
CLUSTER BY severity, anomalyCategory, reviewStatus;
*/
