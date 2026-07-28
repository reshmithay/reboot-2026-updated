-- BigQuery Schema for Blockchain Anomaly Detection System
-- Replace 'your-project.your-dataset' with your actual GCP project and dataset

-- ============================================
-- Transactions Table
-- ============================================
CREATE TABLE IF NOT EXISTS `your-project.your-dataset.transactions` (
    -- Primary identifiers
    id STRING NOT NULL,
    transaction_id STRING NOT NULL,
    transaction_hash STRING NOT NULL,
    
    -- Transaction details
    transaction_type STRING NOT NULL,
    amount NUMERIC NOT NULL,
    currency STRING NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    transaction_status STRING NOT NULL,
    on_chain_status STRING,
    
    -- Account information
    from_account STRING,
    to_account STRING,
    from_wallet_address STRING,
    to_wallet_address STRING,
    wallet_address STRING,
    
    -- Client information
    client_id STRING,
    client_name STRING,
    
    -- Blockchain details
    blockchain_network STRING,
    ledger_type STRING,
    chain_id INT64,
    block_number INT64,
    block_hash STRING,
    token_symbol STRING,
    
    -- Gas and fees
    gas_fee NUMERIC,
    gas_price NUMERIC,
    
    -- Metadata
    correlation_id STRING,
    metadata JSON,
    
    -- Anomaly detection
    anomaly_score NUMERIC,
    is_anomaly BOOL NOT NULL,
    anomaly_codes ARRAY<STRING>,
    risk_score INT64,
    
    -- Audit timestamps
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(transaction_timestamp)
CLUSTER BY client_id, is_anomaly, transaction_type;

-- Create indexes (BigQuery uses clustering instead)
-- Note: BigQuery automatically optimizes queries based on clustering


-- ============================================
-- Client Registry Table
-- ============================================
CREATE TABLE IF NOT EXISTS `your-project.your-dataset.client_registry` (
    -- Primary identifier
    client_id STRING NOT NULL,
    
    -- Basic information
    client_name STRING NOT NULL,
    client_type STRING,
    lei STRING,
    industry_sector STRING,
    country_of_incorporation STRING,
    
    -- Risk and relationship
    risk_tier STRING,
    relationship_manager STRING,
    
    -- Wallet information
    wallet_address STRING,
    wallet_type STRING,
    
    -- Facility details
    facility_type STRING,
    credit_limit NUMERIC,
    daily_deposit_limit NUMERIC,
    daily_withdrawal_limit NUMERIC,
    
    -- Operating parameters
    expected_activity_window STRING,
    authorized_signatories JSON,
    
    -- Compliance status
    kyc_status STRING,
    aml_status STRING,
    
    -- Audit timestamps
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
CLUSTER BY client_id, risk_tier;


-- ============================================
-- Anomaly Master Table
-- ============================================
CREATE TABLE IF NOT EXISTS `your-project.your-dataset.anomaly_master` (
    -- Primary identifier
    anomaly_code STRING NOT NULL,
    
    -- Classification
    category STRING NOT NULL,
    severity STRING NOT NULL,
    risk_score INT64 NOT NULL,
    
    -- Description
    description STRING,
    
    -- Status
    is_active BOOL NOT NULL,
    
    -- Audit timestamps
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
CLUSTER BY category, severity;


-- ============================================
-- Sample Data for Anomaly Master
-- ============================================
INSERT INTO `your-project.your-dataset.anomaly_master` 
    (anomaly_code, category, severity, risk_score, description, is_active, created_at, updated_at)
VALUES
    ('AN001', 'Off-Hours Transaction', 'MEDIUM', 60, 'Transaction occurred outside expected business hours', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('AN002', 'Threshold Deposit', 'HIGH', 85, 'Deposit amount exceeds configured threshold', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('AN003', 'Duplicate Escrow', 'CRITICAL', 95, 'Duplicate escrow payment detected', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('AN004', 'Oracle Manipulation', 'CRITICAL', 98, 'Potential oracle price manipulation detected', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('AN005', 'Daily Limit Breach', 'HIGH', 80, 'Daily transaction limit exceeded', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('AN006', 'Reconciliation Mismatch', 'MEDIUM', 70, 'Reconciliation discrepancy detected', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('AN007', 'Full Withdrawal', 'HIGH', 85, 'Full account withdrawal detected', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('AN008', 'Time Window Violation', 'MEDIUM', 65, 'Transaction outside allowed time window', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('AN009', 'Rapid Transaction', 'MEDIUM', 70, 'Multiple transactions in short time period', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
    ('AN010', 'Unusual Amount', 'MEDIUM', 65, 'Transaction amount deviates from normal pattern', TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());


-- ============================================
-- Views for common queries
-- ============================================

-- View: Recent anomalies with client details
CREATE OR REPLACE VIEW `your-project.your-dataset.v_recent_anomalies` AS
SELECT 
    t.transaction_id,
    t.transaction_hash,
    t.transaction_type,
    t.amount,
    t.currency,
    t.transaction_timestamp,
    t.anomaly_score,
    t.anomaly_codes,
    c.client_name,
    c.risk_tier,
    c.wallet_address
FROM `your-project.your-dataset.transactions` t
LEFT JOIN `your-project.your-dataset.client_registry` c 
    ON t.client_id = c.client_id
WHERE t.is_anomaly = TRUE
ORDER BY t.transaction_timestamp DESC;

-- View: Client transaction summary
CREATE OR REPLACE VIEW `your-project.your-dataset.v_client_transaction_summary` AS
SELECT 
    c.client_id,
    c.client_name,
    c.risk_tier,
    COUNT(t.id) as total_transactions,
    COUNTIF(t.is_anomaly) as anomaly_count,
    SUM(t.amount) as total_amount,
    MAX(t.transaction_timestamp) as last_transaction_date
FROM `your-project.your-dataset.client_registry` c
LEFT JOIN `your-project.your-dataset.transactions` t 
    ON c.client_id = t.client_id
GROUP BY c.client_id, c.client_name, c.risk_tier;

-- View: Daily anomaly statistics
CREATE OR REPLACE VIEW `your-project.your-dataset.v_daily_anomaly_stats` AS
SELECT 
    DATE(transaction_timestamp) as transaction_date,
    COUNT(*) as total_transactions,
    COUNTIF(is_anomaly) as anomaly_count,
    ROUND(AVG(IF(is_anomaly, 1.0, 0.0)) * 100, 2) as anomaly_percentage,
    SUM(amount) as total_amount,
    SUM(IF(is_anomaly, amount, 0)) as anomaly_amount
FROM `your-project.your-dataset.transactions`
GROUP BY DATE(transaction_timestamp)
ORDER BY transaction_date DESC;

-- View: Hourly transaction pattern
CREATE OR REPLACE VIEW `your-project.your-dataset.v_hourly_pattern` AS
SELECT 
    EXTRACT(HOUR FROM transaction_timestamp) as hour_of_day,
    COUNT(*) as transaction_count,
    COUNTIF(is_anomaly) as anomaly_count,
    AVG(amount) as avg_amount
FROM `your-project.your-dataset.transactions`
WHERE transaction_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- View: High-risk clients
CREATE OR REPLACE VIEW `your-project.your-dataset.v_high_risk_clients` AS
SELECT 
    c.client_id,
    c.client_name,
    c.risk_tier,
    c.wallet_address,
    COUNT(t.id) as total_transactions,
    COUNTIF(t.is_anomaly) as anomaly_count,
    ROUND(AVG(IF(t.is_anomaly, 1.0, 0.0)) * 100, 2) as anomaly_percentage,
    SUM(t.amount) as total_volume,
    MAX(t.transaction_timestamp) as last_activity
FROM `your-project.your-dataset.client_registry` c
LEFT JOIN `your-project.your-dataset.transactions` t 
    ON c.client_id = t.client_id
WHERE c.risk_tier IN ('HIGH', 'CRITICAL')
GROUP BY c.client_id, c.client_name, c.risk_tier, c.wallet_address
HAVING COUNTIF(t.is_anomaly) > 0
ORDER BY anomaly_count DESC;


-- ============================================
-- Queries for Analysis
-- ============================================

-- Query: Find clients exceeding daily limits
CREATE OR REPLACE VIEW `your-project.your-dataset.v_daily_limit_violations` AS
WITH daily_volumes AS (
    SELECT 
        client_id,
        DATE(transaction_timestamp) as transaction_date,
        SUM(CASE WHEN transaction_type = 'DEPOSIT' THEN amount ELSE 0 END) as daily_deposits,
        SUM(CASE WHEN transaction_type = 'WITHDRAWAL' THEN amount ELSE 0 END) as daily_withdrawals
    FROM `your-project.your-dataset.transactions`
    GROUP BY client_id, DATE(transaction_timestamp)
)
SELECT 
    dv.client_id,
    c.client_name,
    dv.transaction_date,
    dv.daily_deposits,
    c.daily_deposit_limit,
    dv.daily_withdrawals,
    c.daily_withdrawal_limit,
    CASE 
        WHEN dv.daily_deposits > c.daily_deposit_limit THEN 'DEPOSIT_LIMIT_EXCEEDED'
        WHEN dv.daily_withdrawals > c.daily_withdrawal_limit THEN 'WITHDRAWAL_LIMIT_EXCEEDED'
        ELSE 'WITHIN_LIMITS'
    END as violation_type
FROM daily_volumes dv
JOIN `your-project.your-dataset.client_registry` c 
    ON dv.client_id = c.client_id
WHERE dv.daily_deposits > c.daily_deposit_limit 
   OR dv.daily_withdrawals > c.daily_withdrawal_limit
ORDER BY dv.transaction_date DESC;


-- Query: Anomaly trend by category
CREATE OR REPLACE VIEW `your-project.your-dataset.v_anomaly_trends` AS
SELECT 
    DATE(t.transaction_timestamp) as date,
    am.category,
    am.severity,
    COUNT(*) as occurrence_count,
    SUM(t.amount) as total_amount_flagged,
    ARRAY_AGG(DISTINCT t.client_id) as affected_clients
FROM `your-project.your-dataset.transactions` t,
     UNNEST(t.anomaly_codes) as code
JOIN `your-project.your-dataset.anomaly_master` am 
    ON code = am.anomaly_code
WHERE t.is_anomaly = TRUE
GROUP BY DATE(t.transaction_timestamp), am.category, am.severity
ORDER BY date DESC, occurrence_count DESC;
